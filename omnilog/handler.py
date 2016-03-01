# coding=utf-8
import queue
import threading

import time

from omnilog.notifier import Notifier
from omnilog.logger import Logger


class GeneralLogHandler(threading.Thread):
    """
    This subsystem receives all log messages that need to be saved or notified.
    Its the consumer of the logs queue and the producer of the webpanel queue.
    """
    name = "GenLogHandler"

    def __init__(self, config, log_queue, runner, web_panel_queue):
        super().__init__()
        self.runner = runner
        self.log_queue = log_queue
        self.web_panel_queue = web_panel_queue
        self.logger = Logger()
        self.notifier = Notifier()
        self.config = config['generalHandler']
        self.web_panel_active = config['webPanel']['active']

    def run(self):
        """
        Consumer from log queue and taking action for each log settings.
        """
        self.logger.info("SUB - " + self.name + " - Starting")

        while self.runner.is_set():

            try:
                log = self.log_queue.get(False)
                logPath = self.calc_log_path(log)
                self.write_log(log, logPath)
                if log['systemNotifications']:
                    self.notify_sys(log)
                if self.web_panel_active:
                    self.send_to_webpanel(log)
                self.finish_handling()
                self.logger.info("SUB - " + self.name + " - Log procesed.")
            except queue.Empty:
                time.sleep(1)

    def send_to_webpanel(self, log_data):

        """
        Send log info to the webpanel subsystem.
        :param log_data: JSON object
        """
        self.web_panel_queue.put(log_data)

    def calc_log_path(self, log_data):

        """
        Calculates the name for the log file.
        :param log_data:
        :return: string
        """
        if "logWritePath" in log_data.keys():
            log_write_path = log_data['logWritePath']
        else:
            log_file_name = log_data['name'].replace("\n", "").replace(" ", "_") + ".log".lower()
            log_write_path = self.config['logsPath'] + "/" + log_file_name

        return log_write_path

    def write_log(self, log_data, path):

        """
        Writes log in specifiec path.
        :param log_data:
        :param path:
        """
        with open(path, "a") as log_file:
            log_file.write(log_data['data'] + "\n")

    def notify_sys(self, log_data):

        """
        Send info to the notifications subsystem
        :param log_data:
        """
        self.notifier.send_notify(log_data['name'], log_data['data'])

    def finish_handling(self):

        """
        Finish handler jobs.
        """
        self.log_queue.task_done()
