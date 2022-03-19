#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Filename : option
# @Date     : 2019-08-23
# @Author   : maliao
# @Link     : None


class Option:

    def __init__(self):
        self.options = {
            'verbosity': 0,
            'ask_pass': False,
            'private_key_file': None,
            'remote_user': None,
            'connection': 'smart',
            'timeout': 300,
            'ssh_common_args': '',
            'sftp_extra_args': '',
            'scp_extra_args': '',
            'ssh_extra_args': '',
            'force_handlers': False,
            'flush_cache': None,
            'become': False,
            'become_method': 'sudo',
            'become_user': None,
            'become_ask_pass': False,
            'tags': ('all',),
            'skip_tags': (),
            'check': False,
            'syntax': None,
            'diff': False,
            'listhosts': None,
            'subset': None,
            'extra_vars': (),
            'ask_vault_pass': False,
            'vault_password_files': (), 'vault_ids': (),
            'forks': 5, 'module_path': None, 'listtasks': None, 'listtags': None, 'step': None,
            'start_at_task': None,
            'args': (),
            'remote_tmp':'/tmp/.ansible'
        }

    def set_extra_vars(self, data: dict):
        l = []
        for k,v in data.items():
            l.append("%s=%r" % (k,v))
        self.options['extra_vars'] = tuple(l)

    @property
    def result(self):
        return self.options



if __name__ == '__main__':
    o = Option()
    o.set_extra_vars({'cmd':'ls -al','sh':'daodks'})
    print(o.result)