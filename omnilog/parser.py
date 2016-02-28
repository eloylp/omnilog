import datetime
import re
import select
import threading
import time

from omnilog import ssh_handler


class LogParser(threading.Thread):
    runner = None

    def __init__(self, log, runner, log_queue):
        super().__init__()
        self.runner = runner
        self.log_queue = log_queue
        self.config = log
        self.ssh = ssh_handler.SSHhandler(self.config['ssh'])
        self.interval_secs = 1
        self.recv_buffer = 1024

    def run(self):

        ssh = self.ssh.get_session()
        transport = ssh.get_transport()
        transport.set_keepalive(5)
        channel = transport.open_session()

        channel.exec_command('tail -f ' + self.config['logReadPath'])

        while self.runner.is_set() and transport.is_active():
            time.sleep(self.interval_secs)  # TODO REMOVE THIS ?? SELECT BLOCKS
            rl, wl, xl = select.select([channel], [], [], 0.0)
            if len(rl) > 0:
                data = channel.recv(self.recv_buffer)

                lines = self.get_lines_from_data(data)
                valid_lines = self.check_patterns(lines)

                if len(valid_lines) > 0:

                    for line in valid_lines:

                        self.log_queue.put({"name": self.config['name'],
                                           "data": line,
                                           "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                           "systemNotifications": self.config['systemNotifications']})

        ssh.close()

    def get_lines_from_data(self, data):

        string = data.decode("unicode_escape", "ignore")
        lines = string.split("\n")
        return lines

    def check_patterns(self, lines):

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
