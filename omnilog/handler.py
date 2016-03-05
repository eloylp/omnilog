# coding=utf-8
import queue
import threading

import time

from omnilog.strings import Strings
from omnilog.ipcactions import IPCActions
from omnilog.ipcmessage import IPCMessage
from omnilog.notifier import Notifier
from omnilog.logger import Logger


class GeneralLogHandler(threading.Thread):
    """
    This subsystem receives all log messages that need to be saved or notified.
    Its the consumer of the logs queue and the producer of the webpanel queue.
    """
    name = "SUB-GenLogHandler"

    def __init__(self, config, log_queue, runner, web_panel_queue, vertical_queue):
        super().__init__()
        self.runner = runner
        self.log_queue = log_queue
        self.web_panel_queue = web_panel_queue
        self.logger = Logger()
        self.notifier = Notifier()
        self.config = config['generalHandler']
        self.web_panel_active = config['webPanel']['active']
        self.vertical_queue = vertical_queue

    def run(self):
        """
        Consumer from log queue and taking action for each log settings.
        """
        self.logger.info(self.name + " " + Strings.SUB_SYSTEM_START)

        while self.runner.is_set():

            try:
                log_message = self.log_queue.get(False)
                log_path = self.calc_log_path(log_message)
                self.write_log(log_message, log_path)
                if log_message.system_notifications:
                    self.notify_sys(log_message)
                if self.web_panel_active:
                    self.send_to_webpanel(log_message)
                self.finish_handling()
                self.logger.info(self.name + " " + Strings.LOG_PROCESSED)

            except queue.Empty:
                time.sleep(1)

            except KeyError:
                comm = IPCMessage(self.name, IPCActions.ACTION_SHUTDOWN, Strings.CONFIG_ERROR)
                self.vertical_queue.put(comm)

            except IOError:
                comm = IPCMessage(self.name, IPCActions.ACTION_SHUTDOWN, Strings.IO_ERROR)
                self.vertical_queue.put(comm)

    def send_to_webpanel(self, log_message):

        """
        Send log info to the webpanel subsystem.
        :param log_message: JSON object
        """
        self.web_panel_queue.put(log_message)

    def calc_log_path(self, log_message):

        """
        Calculates the name for the log file.
        :param log_message:
        :return: string        """

        log_file_name = log_message.name.replace("\n", "").replace(" ", "_") + ".log".lower()
        log_write_path = self.config['logsPath'] + "/" + log_file_name

        return log_write_path

    def write_log(self, log_message, path):

        """
        Writes log in specifiec path.
        :param log_message:
        :param path:
        """
        with open(path, "a") as log_file:
            log_file.write(log_message.data + "\n")

    def notify_sys(self, log_message):

        """
        Send info to the notifications subsystem
        :param log_message:
        """
        self.notifier.send_notify(log_message.name, log_message.data)

    def finish_handling(self):

        """
        Finish handler jobs.
        """
        self.log_queue.task_done()
