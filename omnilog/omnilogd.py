#! /usr/bin/env python3
# coding=utf-8

import sys
import threading
import time
from queue import Queue

from omnilog.config import Config
from omnilog.parser import LogParser
from omnilog.handler import GeneralLogHandler
from omnilog.cwatcher import ConfigWatcher
from omnilog.wpanel import WebPanel


class OmniLogD(object):
    """
    This is the main process. It setups config and IPC.
    It starts all services needed to run this app, and is responsible of communication
    between them.
    
    """

    def __init__(self):

        if len(sys.argv) == 2:
            self.config_path = sys.argv[1]
        else:
            self.config_path = "config.json"

        self.booting = True
        self.review_interval = 1

        self.create_events()
        self.create_ipcs()
        self.starter()

    def create_ipcs(self):

        """
        Create the IPC system
        -vertical_queue is intended to comunicate subsystem -> main process.
        -log_queue comunicates log parsers with the handler
        -web_panel_queue passes log information from general handler to web panel subsystem.
        """
        self.vertical_queue = Queue()
        self.log_queue = Queue()
        self.web_panel_queue = Queue()

    def create_events(self):

        """
        It creates the events for signaling start or shutdown in threads.
        """
        self.main_runner = threading.Event()
        self.web_panel_runner = threading.Event()
        self.config_runner = threading.Event()
        self.gen_log_handler_runner = threading.Event()
        self.logs_runner = threading.Event()

    def starter(self):

        """
        Sets by default all events (app services or threads) on.

        """
        self.main_runner.set()
        self.web_panel_runner.set()
        self.config_runner.set()
        self.gen_log_handler_runner.set()
        self.logs_runner.set()

    def run(self):
        """
        The Main function of all the proyect. Its a loop that instantiates all runnable services (threading) with review a
        interval that listens for messages of low level processes (aka threads or app services).
        Its An intermediary between services.
        """
        try:

            config_watcher = ConfigWatcher(self.config_path, self.config_runner, self.vertical_queue)
            config_watcher.start()
            time.sleep(2)

            log_threads = list()

            while self.main_runner.is_set():

                time.sleep(self.review_interval)

                if self.vertical_queue.empty() and self.booting:

                    if self.gen_log_handler_runner.is_set():
                        gen_log_handler = GeneralLogHandler(Config.config_dict, self.log_queue,
                                                            self.gen_log_handler_runner, self.web_panel_queue)
                        gen_log_handler.start()

                    if Config.config_dict['webPanel']['active'] and self.web_panel_runner.is_set():
                        web_panel = WebPanel(self.web_panel_runner, Config.config_dict['webPanel'],
                                             self.web_panel_queue)
                        web_panel.start()

                    if self.logs_runner.is_set():

                        logs = Config.config_dict['logs']

                        for l in logs:

                            if l['active'] is True:
                                t = LogParser(l, self.logs_runner, self.log_queue)
                                log_threads.append(t)
                                t.start()
                                print("Started log watcher for " + l['name'])

                        self.booting = False

                elif not self.vertical_queue.empty():

                    self.manage_com()

        except KeyboardInterrupt:

            self.vertical_queue.put("SHUTDOWN")

    def manage_com(self):

        """
        This function is responsible of handling messages arrived from the different app services.
        This queue needs to be based on topics because the main process needs to understand from what service
        come each message.
        """
        com = self.vertical_queue.get()
        if com == 'RESTART':
            self.restart()
        elif com == 'SHUTDOWN':
            self.shutdown()

    def restart(self):

        """
        The restart operation. It send the event to stop gracefully stop all threads, waits for
        job ending and then start it again.
        """
        print("Reset event triggered. Restarting app")
        self.logs_runner.clear()
        time.sleep(2)
        self.web_panel_runner.clear()
        self.gen_log_handler_runner.clear()
        time.sleep(2)
        self.web_panel_runner.set()
        self.gen_log_handler_runner.set()
        self.logs_runner.set()
        self.booting = True

    def shutdown(self):
        """
        The shutdown operation. Same procedure as restart, but this time the main loop will not do more
        review and exit.
        """
        print("Shutting down app")
        self.logs_runner.clear()
        time.sleep(2)
        self.web_panel_runner.clear()
        self.gen_log_handler_runner.clear()
        self.main_runner.clear()


if __name__ == '__main__':
    w = OmniLogD()
    w.run()
