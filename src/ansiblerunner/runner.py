# ~*~ coding: utf-8 ~*~

import os
import shutil
from collections import namedtuple

from ansible import context
from ansible.module_utils.common.collections import ImmutableDict
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.vars.manager import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.playbook.play import Play
from ansible.inventory.manager import InventoryManager
import ansible.constants as C
from src.redisbase import RedisQueue
from .callback import (
    AdHocResultCallback,
    PlaybookResultCallBack,
    CommandResultCallback,
    CmdRedisResultCallback
)
from .exceptions import AnsibleError
from .option import Option
from .inventory import BaseInventory

__all__ = ["AdHocRunner", "PlayBookRunner", "CommandRunner"]
C.HOST_KEY_CHECKING = False

Options = namedtuple('Options', [
    'listtags', 'listtasks', 'listhosts', 'syntax', 'connection',
    'module_path', 'forks', 'remote_user', 'private_key_file', 'timeout',
    'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args',
    'scp_extra_args', 'become', 'become_method', 'become_user',
    'verbosity', 'check', 'extra_vars', 'playbook_path', 'passwords',
    'diff', 'gathering', 'remote_tmp',
])


def get_default_options():
    options = dict(
        syntax=False,
        timeout=30,
        connection='ssh',
        forks=70,
        remote_user='root',
        private_key_file=None,
        become=None,
        become_method=None,
        become_user=None,
        verbosity=1,
        check=False,
        diff=False,
        gathering='implicit',
        remote_tmp='/tmp/.ansible'
    )
    return options


class PlayBaseRunner:
    """
    用于执行AnsiblePlaybook的接口.简化Playbook对象的使用.
    """

    # Default results callback
    results_callback_class = PlaybookResultCallBack
    loader_class = DataLoader
    variable_manager_class = VariableManager

    def __init__(self, inventory=None, options=None, playbook_path=None,uuid='uuid'):
        C.RETRY_FILES_ENABLED = False

        self.options = options
        context.CLIARGS = ImmutableDict(self.options)
        self.loader = self.loader_class()
        if inventory:
            self.inventory = inventory
        else:
            self.inventory = InventoryManager(self.loader)
        self.results_callback = self.results_callback_class()
        self.playbook_path = playbook_path
        self.variable_manager = self.variable_manager_class(
            loader=self.loader, inventory=self.inventory,

        )
        self.passwords = None
        self.uuid = uuid

    def get_result_callback(self, file_obj=None):
        return self.__class__.results_callback_class()

    def run(self):

        executor = PlaybookExecutor(
            playbooks=[self.playbook_path],
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            passwords={"conn_pass": self.passwords}
        )

        self.results_callback = self.get_result_callback()
        self.results_callback.rq = RedisQueue(self.uuid)

        if executor._tqm:
            executor._tqm._stdout_callback = self.results_callback
        executor.run()
        executor._tqm.cleanup()
        return executor._tqm._stdout_callback


class PlayBookRunner:

    def __init__(self, hostname, path, options={}, inventory=None):
        self.hostname = hostname

        option = options
        option.update({'forks':70})
        self.options = self.set_option(option)
        if inventory:

            if isinstance(inventory,dict):
                self.inventory = self.set_inventory(**inventory)
            if isinstance(inventory,list):
                self.inventory = self.set_inventorys(inventory)
        else:
            self.inventory = inventory
        self.path = path

    def set_inventory(self, ip, port, username, password):
        host_data = [
            {
                "hostname": self.hostname,
                "ip": ip,
                "port": port,
                "username": username,
                "password": password,
            },
        ]
        inventory = BaseInventory(host_data)
        return inventory

    def set_inventorys(self, inventory_data):

        host_data = []
        for d in inventory_data:


            host_data.append({
                "hostname": d['hostname'],
                "ip": d['ip'],
                "port": d['port'],
                "username": d['username'],
                "password": d['private_key'],
            })

        inventory = BaseInventory(host_data)
        return inventory

    def set_option(self, options: dict):
        o = Option()
        o.set_extra_vars(options)
        return o.result

    def run(self):


        prunner = PlayBaseRunner(
            playbook_path=self.path,
            options=self.options,
            inventory=self.inventory,
            uuid=self.hostname
        )

        # print(self.hostname)

        ret = prunner.run()
        # print(ret.result)
        self.result = ret.result

        return prunner.results_callback.log

    @property
    def get_result(self):
        return self.result


class AdHocRunner:
    """
    ADHoc Runner接口
    """
    results_callback_class = AdHocResultCallback
    results_callback = None
    loader_class = DataLoader
    variable_manager_class = VariableManager
    default_options = get_default_options()
    command_modules_choices = ('shell', 'raw', 'command', 'script', 'win_shell')

    def __init__(self, inventory, options=None):
        self.options = self.update_options(options)
        self.inventory = inventory
        self.loader = DataLoader()
        self.variable_manager = VariableManager(
            loader=self.loader, inventory=self.inventory
        )

    def get_result_callback(self, file_obj=None):
        return self.__class__.results_callback_class()

    @staticmethod
    def check_module_args(module_name, module_args=''):
        if module_name in C.MODULE_REQUIRE_ARGS and not module_args:
            err = "No argument passed to '%s' module." % module_name
            raise AnsibleError(err)

    def check_pattern(self, pattern):
        if not pattern:
            raise AnsibleError("Pattern `{}` is not valid!".format(pattern))
        if not self.inventory.list_hosts("all"):
            raise AnsibleError("Inventory is empty.")
        if not self.inventory.list_hosts(pattern):
            raise AnsibleError(
                "pattern: %s  dose not match any hosts." % pattern
            )

    def clean_args(self, module, args):
        if not args:
            return ''
        if module not in self.command_modules_choices:
            return args
        if isinstance(args, str):
            if args.startswith('executable='):
                _args = args.split(' ')
                executable, command = _args[0].split('=')[1], ' '.join(_args[1:])
                args = {'executable': executable, '_raw_params': command}
            else:
                args = {'_raw_params': args}
            return args
        else:
            return args

    def clean_tasks(self, tasks):
        cleaned_tasks = []
        for task in tasks:
            module = task['action']['module']
            args = task['action'].get('args')
            cleaned_args = self.clean_args(module, args)
            task['action']['args'] = cleaned_args
            self.check_module_args(module, cleaned_args)
            cleaned_tasks.append(task)
        return cleaned_tasks

    def update_options(self, options):
        _options = {k: v for k, v in self.default_options.items()}
        if options and isinstance(options, dict):
            _options.update(options)
        return _options

    def run(self, tasks, pattern, play_name='Ansible Ad-hoc', gather_facts='no', uuid='uuid'):
        """
        :param tasks: [{'action': {'module': 'shell', 'args': 'ls'}, ...}, ]
        :param pattern: all, *, or others
        :param play_name: The play name
        :param gather_facts:
        :return:
        """
        self.check_pattern(pattern)
        self.results_callback = self.get_result_callback()

        cleaned_tasks = self.clean_tasks(tasks)
        context.CLIARGS = ImmutableDict(self.options)

        play_source = dict(
            name=play_name,
            hosts=pattern,
            gather_facts=gather_facts,
            tasks=cleaned_tasks
        )

        play = Play().load(
            play_source,
            variable_manager=self.variable_manager,
            loader=self.loader,
        )

        # 為self.results_callback class 加上rq
        self.results_callback.rq = RedisQueue(uuid)
        #

        tqm = TaskQueueManager(
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            stdout_callback=self.results_callback,
            passwords={"conn_pass": self.options.get("password", "")}
        )

        try:
            tqm.run(play)
            return self.results_callback
        except Exception as e:
            raise AnsibleError(e)
        finally:
            if tqm is not None:
                tqm.cleanup()
            shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)


class CommandRunner(AdHocRunner):
    results_callback_class = CommandResultCallback
    modules_choices = ('shell', 'raw', 'command', 'script')

    def execute(self, cmd, pattern, module='shell', uuid='uuid'):
        if module and module not in self.modules_choices:
            raise AnsibleError("Module should in {}".format(self.modules_choices))

        tasks = [
            {"action": {"module": module, "args": cmd}}
        ]
        return self.run(tasks, pattern, play_name=cmd, uuid=uuid)
