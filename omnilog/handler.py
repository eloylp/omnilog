# coding=utf-8

import threading

from omnilog.notifier import Notifier


class GeneralLogHandler(threading.Thread):
    """
    This subsystem receives all log messages that need to be saved or notified.
    Its the consumer of the logs queue and the producer of the webpanel queue.
    """

    def __init__(self, config, log_queue, runner, web_panel_queue):
        super().__init__()
        self.runner = runner
        self.log_queue = log_queue
        self.web_panel_queue = web_panel_queue
        self.notifier = Notifier()
        self.config = config['generalHandler']
        self.web_panel_active = config['webPanel']['active']

    def run(self):
        """
        Consumer from log queue and taking action for each log settings.
        """
        while self.runner.is_set():
            log = self.log_queue.get(True)
            logPath = self.calc_log_path(log)
            self.write_log(log, logPath)
            if log['systemNotifications']:
                self.notify_sys(log)
            if self.web_panel_active:
                self.send_to_webpanel(log)
            self.finish_handling()

    def send_to_webpanel(self, logData):

        """
        Send log info to the webpanel subsystem.
        :param logData: JSON object
        """
        self.web_panel_queue.put(logData)

    def calc_log_path(self, logData):

        """
        Calculates the name for the log file.
        :param logData:
        :return: string
        """
        if "logWritePath" in logData.keys():
            log_write_path = logData['logWritePath']
        else:
            log_file_name = logData['name'].replace("\n", "").replace(" ", "_") + ".log".lower()
            log_write_path = self.config['logsPath'] + "/" + log_file_name

        return log_write_path

    def write_log(self, logData, path):

        """
        Writes log in specifiec path.
        :param logData:
        :param path:
        """
        with open(path, "a") as log_file:
            log_file.write(logData['data'] + "\n")

    def notify_sys(self, logData):

        """
        Send info to the notifications subsystem
        :param logData:
        """
        self.notifier.send_notify(logData['name'], logData['data'])

    def finish_handling(self):

        """
        Finish handler jobs.
        """
        self.log_queue.task_done()
