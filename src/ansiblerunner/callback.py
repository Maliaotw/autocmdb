# ~*~ coding: utf-8 ~*~

import datetime
import json
from collections import defaultdict

from ansible import constants
from ansible.plugins.callback import CallbackBase
from ansible.plugins.callback.default import CallbackModule
from ansible.plugins.callback.minimal import CallbackModule as CMDCallBackModule


class CallbackMixin:
    def __init__(self, display=None):
        # result_raw example: {
        #   "ok": {"hostname": {"task_name": {}，...},..},
        #   "failed": {"hostname": {"task_name": {}..}, ..},
        #   "unreachable: {"hostname": {"task_name": {}, ..}},
        #   "skipped": {"hostname": {"task_name": {}, ..}, ..},
        # }
        # results_summary example: {
        #   "contacted": {"hostname": {"task_name": {}}, "hostname": {}},
        #   "dark": {"hostname": {"task_name": {}, "task_name": {}},...,},
        #   "success": True
        # }
        self.results_raw = dict(
            ok=defaultdict(dict),
            failed=defaultdict(dict),
            unreachable=defaultdict(dict),
            skippe=defaultdict(dict),
        )
        self.results_summary = dict(
            contacted=defaultdict(dict),
            dark=defaultdict(dict),
            success=True
        )
        self.results = {
            'raw': self.results_raw,
            'summary': self.results_summary,
        }
        super().__init__()
        if display:
            self._display = display
        self._display.columns = 79

    def display(self, msg):
        self._display.display(msg)

    def gather_result(self, t, result):
        self._clean_results(result._result, result._task.action)
        host = result._host.get_name()
        task_name = result.task_name
        task_result = result._result

        self.results_raw[t][host][task_name] = task_result
        self.clean_result(t, host, task_name, task_result)


class AdHocResultCallback(CallbackMixin, CallbackModule, CMDCallBackModule):
    """
    Task result Callback
    """

    def clean_result(self, t, host, task_name, task_result):
        contacted = self.results_summary["contacted"]
        dark = self.results_summary["dark"]

        if task_result.get('rc') is not None:
            cmd = task_result.get('cmd')
            if isinstance(cmd, list):
                cmd = " ".join(cmd)
            else:
                cmd = str(cmd)
            detail = {
                'cmd': cmd,
                'stderr': task_result.get('stderr'),
                'stdout': task_result.get('stdout'),
                'rc': task_result.get('rc'),
                'delta': task_result.get('delta'),
                'msg': task_result.get('msg', '')
            }
        else:
            detail = {
                "changed": task_result.get('changed', False),
                "msg": task_result.get('msg', '')
            }

        if t in ("ok", "skipped"):
            contacted[host][task_name] = detail
        else:
            dark[host][task_name] = detail

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.results_summary['success'] = False
        self.gather_result("failed", result)

        if result._task.action in constants.MODULE_NO_JSON:
            CMDCallBackModule.v2_runner_on_failed(
                self,
                result, ignore_errors=ignore_errors
            )
        else:
            super().v2_runner_on_failed(
                result, ignore_errors=ignore_errors
            )

    def v2_runner_on_ok(self, result):
        self.gather_result("ok", result)
        if result._task.action in constants.MODULE_NO_JSON:
            CMDCallBackModule.v2_runner_on_ok(self, result)
        else:
            super().v2_runner_on_ok(result)

    def v2_runner_on_skipped(self, result):
        self.gather_result("skipped", result)
        super().v2_runner_on_skipped(result)

    def v2_runner_on_unreachable(self, result):
        self.results_summary['success'] = False
        self.gather_result("unreachable", result)
        super().v2_runner_on_unreachable(result)

    def display_skipped_hosts(self):
        pass

    def display_ok_hosts(self):
        pass

    def display_failed_stderr(self):
        pass


class CommandResultCallback(AdHocResultCallback):
    """
    Command result callback

    results_command: {
      "cmd": "",
      "stderr": "",
      "stdout": "",
      "rc": 0,
      "delta": 0:0:0.123
    }
    """

    def __init__(self, display=None, **kwargs):

        self.results_command = dict()
        self.log = []

        super().__init__(display)

        # print('self.foo',self.foo)

    def gather_result(self, t, res):
        super().gather_result(t, res)
        self.gather_cmd(t, res)

    def v2_playbook_on_play_start(self, play):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg = '$ {} ({})'.format(play.name, now)
        self._play = play
        self._display.banner(msg)
        self.log.append("%s\r\n" % msg)
        self.rq.put("%s\r\n" % msg)

        # print('self._play.name', self._play.name)

    def v2_runner_on_ok(self, result):
        print('v2_runner_item_on_ok')
        self.results_summary['success'] = True

        # print(result._result)
        ret = "\033[1;33m%s | OK | rc=%s => \r\n%s\r\n\033[0m" % (
            result._host.get_name(), result._result.get("rc"), result._result.get("stdout").replace('\n', '\r\n'))

        self._display.display(ret)
        self.log.append(ret)
        self.rq.put(ret)

    def v2_runner_on_unreachable(self, result):
        self.results_summary['success'] = False
        self.gather_result("unreachable", result)
        msg = result._result.get("msg")

        if not msg:
            msg = json.dumps(result._result, indent=4)

        ret = "%s | FAILED! => \r\n%s\r\n" % (result._host.get_name(), msg,)

        self._display.display(ret, color=constants.COLOR_ERROR)
        self.log.append("\033[1;31m%s\r\n\033[0m" % ret)
        self.rq.put("\033[1;31m%s\r\n\033[0m" % ret)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.results_summary['success'] = False
        self.gather_result("failed", result)
        msg = result._result.get("msg", '')
        stderr = result._result.get("stderr")
        if stderr:
            msg += '\n' + stderr
        module_stdout = result._result.get("module_stdout")
        if module_stdout:
            msg += '\n' + module_stdout
        if not msg:
            msg = json.dumps(result._result, indent=4)

        ret = "%s | FAILED! => \r\n%s\r\n" % (result._host.get_name(), msg,)

        self._display.display(ret, color=constants.COLOR_ERROR)
        self.log.append("\033[1;31m%s\r\n\033[0m" % ret)
        self.rq.put("\033[1;31m%s\r\n\033[0m" % ret)

        # print('self._play.name',self._play.name)

    def _print_task_banner(self, task):
        pass

    def gather_cmd(self, t, res):
        host = res._host.get_name()
        cmd = {}
        if t == "ok":
            cmd['cmd'] = res._result.get('cmd')
            cmd['stderr'] = res._result.get('stderr')
            cmd['stdout'] = res._result.get('stdout')
            cmd['rc'] = res._result.get('rc')
            cmd['delta'] = res._result.get('delta')
        else:
            cmd['err'] = "Error: {}".format(res)

        self.results_command[host] = cmd


class CmdRedisResultCallback(CommandResultCallback):

    def v2_playbook_on_play_start(self, play):
        super().v2_playbook_on_play_start(play)

    def v2_runner_on_unreachable(self, result):
        super().v2_runner_on_unreachable(result)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        super().v2_runner_on_failed(result, ignore_errors=ignore_errors)


class PlaybookResultCallBack(CallbackBase):
    CALLBACK_VERSION = 2.0

    def __init__(self, *args, **kwargs):
        super(PlaybookResultCallBack, self).__init__(*args, **kwargs)
        self.task_ok = {}
        self.task_skipped = {}
        self.task_failed = {}
        self.task_status = {}
        self.task_unreachable = {}
        self.task_changed = {}
        self.task_result = {}
        self.log = []

    def v2_playbook_on_task_start(self, task, is_conditional):
        '''
        TASK [nginx : install nginx]

        '''
        msg = "TASK [%s] ***************************************************" % task.name
        self._display.banner(msg)
        self.log.append(msg)
        self.rq.put(msg)

        super().v2_playbook_on_task_start(task, is_conditional)

    def v2_playbook_on_start(self, playbook):
        # print("v2_playbook_on_start")
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # print(dir(playbook))

        msg = '$ {} ({})'.format(playbook, now)
        self._play = playbook
        self._display.banner(msg)
        self.log.append(msg)
        self.rq.put(msg)
        super().v2_playbook_on_start(playbook)

    def v2_runner_on_ok(self, result, *args, **kwargs):
        data1 = {
            'msg': '',
            'invocation': {
                'module_args': {
                    'lock_timeout': 30, 'update_cache': False, 'disable_excludes': None, 'exclude': [],
                    'allow_downgrade': False, 'disable_gpg_check': False, 'conf_file': None,
                    'use_backend': 'auto', 'state': 'present', 'disablerepo': [], 'releasever': None,
                    'skip_broken': False, 'autoremove': False, 'download_dir': None, 'enable_plugin': [],
                    'installroot': '/', 'install_weak_deps': True, 'name': ['epel-release'],
                    'download_only': False, 'bugfix': False, 'list': None, 'install_repoquery': True,
                    'update_only': False, 'disable_plugin': [], 'enablerepo': [], 'security': False,
                    'validate_certs': True}
            },
            'changed': False,
            'results': ['epel-release-7-11.noarch providing epel-release is already installed'],
            'rc': 0,
            '_ansible_no_log': False
        }
        data2 = {
            'changed': True,
            'results': [
                'Loaded plugins: fastestmirror\n'
                'Resolving Dependencies\n'
                '--> Running transaction check\n'
                '---> Package nginx.x86_64 1:1.12.2-3.el7 will be erased\n'
                '--> Processing Dependency: nginx for package: 1:nginx-mod-mail-1.12.2-3.el7.x86_64\n'
                '--> Processing Dependency: nginx for package: 1:nginx-mod-http-image-filter-1.12.2-3.el7.x86_64\n'
                '--> Processing Dependency: nginx for package: 1:nginx-mod-stream-1.12.2-3.el7.x86_64\n'
                '--> Processing Dependency: nginx for package: 1:nginx-mod-http-geoip-1.12.2-3.el7.x86_64\n'
                '--> Processing Dependency: nginx for package: 1:nginx-mod-http-perl-1.12.2-3.el7.x86_64\n'
                '........'
            ],
            'msg': '',
            'rc': 0,
            'invocation': {
                'module_args': {
                    'lock_timeout': 30, 'update_cache': False, 'disable_excludes': None, 'exclude': [],
                    'allow_downgrade': False, 'disable_gpg_check': False, 'conf_file': None,
                    'use_backend': 'auto', 'state': 'absent', 'disablerepo': [], 'releasever': None,
                    'skip_broken': False, 'autoremove': False, 'download_dir': None, 'enable_plugin': [],
                    'installroot': '/', 'install_weak_deps': True, 'name': ['nginx'],
                    'download_only': False, 'bugfix': False, 'list': None, 'install_repoquery': True,
                    'update_only': False, 'disable_plugin': [], 'enablerepo': [], 'security': False,
                    'validate_certs': True}
            },
            'changes': {'removed': ['nginx']},
            '_ansible_no_log': False
        }

        data3 = {
            'changed': True, 'end': '2019-09-05 16:53:34.920614', 'stdout': '/root', 'cmd': 'pwd', 'rc': 0,
            'start': '2019-09-05 16:53:34.894672', 'stderr': '', 'delta': '0:00:00.025942', 'invocation': {
                'module_args': {'creates': None, 'executable': None, '_uses_shell': True, 'strip_empty_ends': True,
                                '_raw_params': 'pwd', 'removes': None, 'argv': None, 'warn': True, 'chdir': None,
                                'stdin_add_newline': True, 'stdin': None}}, 'stdout_lines': ['/root'],
            'stderr_lines': [], '_ansible_no_log': False
        }
        data4 = {
            'msg':
                {
                    'changed': True, 'end': '2019-09-05 16:53:34.920614', 'stdout': '/root', 'cmd': 'pwd', 'rc': 0,
                    'start': '2019-09-05 16:53:34.894672', 'stderr': '', 'delta': '0:00:00.025942',
                    'stdout_lines': ['/root'], 'stderr_lines': [], 'failed': False
                },
            '_ansible_verbose_always': True,
            '_ansible_no_log': False, 'changed': False}

        self.task_ok[result._host.get_name()] = result
        self.result = result._result
        # print('ok')
        # print(result._result)

        if self.result['changed']:
            status = 'changed'  # 黃色
            msg = "\033[1;33m%s: [%s]\033[0m" % (status, result._host.get_name())
        else:
            status = 'ok'  # 綠色
            msg = "\033[1;32m%s: [%s]\033[0m" % (status, result._host.get_name())

        self._display.display("%s: [%s]" % (status, result._host.get_name()))
        self.log.append("%s\r\n" % msg)
        self.rq.put("%s\r\n" % msg)

        if result._result.get('msg'):
            self._display.display(result._result['msg']['stdout'])
            self.log.append(result._result['msg']['stdout'].replace('\n', '\r\n'))
            self.rq.put(result._result['msg']['stdout'].replace('\n', '\r\n'))

    def v2_runner_on_failed(self, result, *args, **kwargs):
        self.task_failed[result._host.get_name()] = result

        '''
        {'changed': True, 'end': '2019-09-05 12:08:25.083468', 'stdout': '', 'cmd': 'asdds', 'delta': '0:00:00.026301', 'stderr': '/bin/sh: asdds：命令找不到', 'rc': 127, 'invocation': {'module_args': {'creates': None, 'executable': None, '_uses_shell': True, 'strip_empty_ends': True, '_raw_params': 'asdds', 'removes': None, 'argv': None, 'warn': True, 'chdir': None, 'stdin_add_newline': True, 'stdin': None}}, 'start': '2019-09-05 12:08:25.057167', 'msg': 'non-zero return code', 'stdout_lines': [], 'stderr_lines': ['/bin/sh: asdds：命令找不到'], '_ansible_no_log': False}
        '''

        msg = 'fatal: [%s]: FAILED! => %s' % (result._host.get_name(), str(result._result))
        self._display.display(msg, color=constants.COLOR_ERROR)
        self.log.append("\033[1;31m%s\r\n\033[0m" % msg)
        self.rq.put("\033[1;31m%s\r\n\033[0m" % msg)

    def v2_runner_on_unreachable(self, result):
        self.task_unreachable[result._host.get_name()] = result
        # msg = result._result.get("msg")
        # print(result._result)
        '''
        [2019-09-05 10:31:47,698: WARNING/ForkPoolWorker-9] {'unreachable': True, 'msg': 'Failed to connect to the host via ssh: ssh: connect to host 43.54.62.123 port 2222: Operation timed out', 'changed': False}
        '''

        msg = 'fatal: [%s]: UNREACHABLE! => %s' % (result._host.get_name(), str(result._result))

        self._display.display(msg, color=constants.COLOR_ERROR)
        self.log.append("\033[1;31m%s\r\n\033[0m" % msg)
        self.rq.put("\033[1;31m%s\r\n\033[0m" % msg)

    def v2_runner_on_skipped(self, result):
        self.task_skipped[result._host.get_name()] = result

    def v2_runner_on_changed(self, result):
        self.task_changed[result._host.get_name()] = result
        self.task_ok[result._host.get_name()] = result
        self.result = result._result
        ret = "%s | CHANGED | rc=%s => \r\n%s\r\n" % (
            result._host.get_name(), result._result.get("rc"), result._result.get("stdout").replace('\n', '\r\n'))
        self._display.display(ret)
        self.log.append("%s\r\n" % ret)
        self.rq.put("%s\r\n" % ret)

    def v2_playbook_on_stats(self, stats):
        hosts = sorted(stats.processed.keys())

        color = {
            'ok': '\033[1;32mok=%s\033[0m',
            'changed': '\033[1;33mchanged=%s\033[0m',
            'unreachable': '\033[1;31munreachable=%s\033[0m',
            'failures': '\033[1;31mfailed=%s\033[0m',
            'skipped': '%s',
            'rescued': '%s',
            'ignored': '%s',

        }

        for h in hosts:
            t = stats.summarize(h)
            self.task_status[h] = {
                "ok": t['ok'],
                "changed": t['changed'],
                "unreachable": t['unreachable'],
                "skipped": t['skipped'],
                "failed": t['failures']
            }

            data = {}
            for k, v in t.items():
                if int(v) > 0:
                    if k in ['unreachable', 'failures']:
                        h = "\033[1;31m%s\033[0m" % h
                    data[k] = color[k] % v
                else:
                    data[k] = "%s=%s" % (k, v)

            self.task_result[h] = data

        # print(self.res)
        # print("self.task_result")
        # print(self.task_result)
        '''
        {'jumpserver-web1': {'ok': 1, 'changed': 0, 'unreachable': 0, 'skipped': 0, 'failed': 1}}
        '''
        ret = ["PLAY RECAP *********************************************************************\r\n"]
        msg = "%s\t\t\t: %s\t%s\t%s\t%s"
        for k, v in self.task_result.items():
            '''
            PLAY RECAP *********************************************************************
            jumpserver1                : ok=0    changed=0    unreachable=1    failed=0
            jumpserver2                : ok=0    changed=0    unreachable=1    failed=0
            jumpserver3                : ok=10   changed=3    unreachable=0    failed=0
            '''
            # print(k,v)

            ret.append(msg % (k, v['ok'], v['changed'], v['unreachable'], v['failures']))

        ret = "\r\n".join(ret)
        self._display.display(ret)
        self.log.append(("%s" % ret))
        self.rq.put("%s" % ret)
