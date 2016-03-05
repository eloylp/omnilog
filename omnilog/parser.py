# coding=utf-8

import datetime
import re
import select
import threading
import time
from paramiko import SSHException

from omnilog.strings import Strings
from omnilog.ipcactions import IPCActions
from omnilog.ipcmessage import IPCMessage
from omnilog.logmessage import LogMessage
from omnilog.sshh import SSHhandler
from omnilog.logger import Logger


class LogParser(threading.Thread):
    """
    This subsystem may run for each log instance.
    Its responsibility is to pull changes from paramiko channel,
    split it into lines and check user defined regex over them.
    After all , it queues the result (if valid) into the general
    log handler queue.SS
    """
    name = "SUB-LogParser"
    runner = None

    def __init__(self, log, runner, log_queue, vertical_queue):
        super().__init__()
        self.runner = runner
        self.log_queue = log_queue
        self.config = log
        self.ssh = SSHhandler(self.config['ssh'])
        self.logger = Logger()
        self.interval_secs = 1
        self.recv_buffer = 1024
        self.vertical_queue = vertical_queue

    def run(self):

        try:

            self.logger.info(self.name + " " + Strings.SUB_SYSTEM_START)

            ssh = self.ssh.get_session()
            transport = ssh.get_transport()
            transport.set_keepalive(5)
            channel = transport.open_session()

            channel.exec_command('tail -f ' + self.config['logReadPath'])

            while self.runner.is_set() and transport.is_active():
                time.sleep(self.interval_secs)

                rl, wl, xl = select.select([channel], [], [], 0.0)
                if len(rl) > 0:
                    data = channel.recv(self.recv_buffer)

                    lines = self.get_lines_from_data(data)
                    valid_lines = self.check_patterns(lines)

                    if len(valid_lines) > 0:

                        for line in valid_lines:
                            self.logger.info(self.name + " " + Strings.PARSER_VALID_LOG_REACHED)
                            self.log_queue.put(
                                LogMessage(
                                    self.config['name'],
                                    line,
                                    self.config['systemNotifications'],
                                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                ))

            ssh.close()

        except KeyError:

            ipc_msg = IPCMessage(self.name, IPCActions.ACTION_SHUTDOWN, Strings.CONFIG_ERROR)
            self.vertical_queue.put(ipc_msg)

        except SSHException:

            ipc_msg = IPCMessage(self.name, IPCActions.ACTION_SHUTDOWN, Strings.SSH_ERROR)
            self.vertical_queue.put(ipc_msg)

    def get_lines_from_data(self, data):

        """
        Transform data received from ssh channel to a list of lines.
        :param data: bytes
        :return: list
        """
        string = data.decode("unicode_escape", "ignore")
        lines = string.split("\n")
        return lines

    def check_patterns(self, lines):

        """
        Validates log lines against user defined regex (only if defined).
        Returns the result list.

        :param lines: list
        :return: list
        """
        not_black_listed = []
        valid_lines = []

        if "ignorePatterns" in self.config.keys() and len(self.config['ignorePatterns']) > 0:
            for l in lines:
                for p in self.config['ignorePatterns']:
                    if not re.search(p, l):
                        not_black_listed.append(l)
        else:
            not_black_listed = lines

        if "patterns" in self.config.keys() and len(self.config['patterns']) > 0:

            for l in not_black_listed:
                for p in self.config['patterns']:
                    if re.search(p, l):
                        valid_lines.append(l)
        else:
            valid_lines = not_black_listed
        result = [v for v in valid_lines if v != '']
        return result
