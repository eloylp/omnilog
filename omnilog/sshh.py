# coding=utf-8

import io
import paramiko


class SSHhandler(object):
    """
    Our SSH wrapper class for paramiko. Its not only a wrapper class.
    It has some responsibility , that is , return the proper ssh connection
    object taking in count the config passed.
    """

    def __init__(self, config):
        self.config = config

    def get_session(self):

        """
        Determines what auth method need to use.
        :return: object connection
        """
        if "password" in self.config.keys():
            ssh = self.connect_with_password()
        elif "privateKey" in self.config.keys():
            ssh = self.connect_with_private_key()
        else:
            ssh = self.connect_with_system_keys()

        return ssh

    def connect_with_password(self):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.config['hostname'], password=self.config['password'],
                    username=self.config['username'], port=self.config['port'])

        return ssh

    def connect_with_system_keys(self):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.config['hostname'], username=self.config['username'], port=self.config['port'])

        return ssh

    def connect_with_private_key(self):
        pkfile = io.StringIO(open(self.config['privateKey']['path'], 'r').read())
        pkey = paramiko.RSAKey.from_private_key(pkfile, password=self.config['privateKey']['passphrase'])
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.config['hostname'], username=self.config['username'], port=self.config['port'],
                    pkey=pkey, look_for_keys=False)

        return ssh
