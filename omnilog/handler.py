import threading

from omnilog.notifier import Notifier


class GeneralLogHandler(threading.Thread):
    def __init__(self, config, log_queue, runner, web_panel_queue):
        super().__init__()
        self.runner = runner
        self.log_queue = log_queue
        self.web_panel_queue = web_panel_queue
        self.notifier = Notifier()
        self.config = config['generalHandler']
        self.web_panel_active = config['webPanel']['active']

    def run(self):
        while self.runner.is_set():
            log = self.log_queue.get(True)
            logPath = self.calc_log_path(log)
            self.write_log(log, logPath)
            if log['systemNotifications']:
                self.notify_sys(log)
            if self.web_panel_active:
                self.web_panel_queue.put(log)
            self.finish_handling()

    def calc_log_path(self, logData):

        if "logWritePath" in logData.keys():
            log_write_path = logData['logWritePath']
        else:
            log_file_name = logData['name'].replace("\n", "").replace(" ", "_") + ".log".lower()
            log_write_path = self.config['logsPath'] + "/" + log_file_name

        return log_write_path

    def write_log(self, logData, path):

        log_file = open(path, "a")
        log_file.write(logData['data'] + "\n")
        log_file.close()

    def notify_sys(self, logData):

        self.notifier.send_notify(logData['name'], logData['data'])

    def finish_handling(self):

        self.log_queue.task_done()
