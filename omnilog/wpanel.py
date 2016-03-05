# coding=utf-8

import json
import queue
import threading

import time

from omnilog.strings import Strings
from omnilog.ipcactions import IPCActions
from omnilog.ipcmessage import IPCMessage
from omnilog.server import HTTPServer
from omnilog.logger import Logger


class WebPanel(threading.Thread):
    """
    This runnable has the responsibility or maintain the webpanel updated.
    It starts up the web server subsystem and forwards IPC signaling between the
    main process and the webserver.
    It consumes the web_panel_queue.
    """
    name = "SUB-WebPanel"
    runner = None

    def __init__(self, runner, config, web_panel_queue, vertical_queue):
        super().__init__()
        self.runner = runner
        self.logger = Logger()
        self.config = config
        self.web_panel_queue = web_panel_queue
        self.HTTP_server = HTTPServer
        self.data = {"config": self.config['frontEndConfig'], "logs": []}
        self.vertical_queue = vertical_queue

    def run(self):

        self.logger.info(self.name + " " + Strings.SUB_SYSTEM_START)
        web_server = self.HTTP_server(self.config['webServer'], self.runner, self.vertical_queue)
        web_server.start()

        while self.runner.is_set():

            try:
                log_message = self.web_panel_queue.get(False)

                self.logger.info(self.name + " " + Strings.WEBPANEL_PUBLISH)
                if len(self.data['logs']) >= self.config['maxEntries']:
                    self.data['logs'].pop()
                self.data['logs'].insert(0, log_message.get_object())
                with open(self.config['dataOutput'] + "/" + "logs.json", 'w') as f:
                    json.dump(self.data, f, indent=4)
            except queue.Empty:
                time.sleep(1)
            except KeyError:
                ipc_msg = IPCMessage(self.name, IPCActions.ACTION_SHUTDOWN, Strings.CONFIG_ERROR)
                self.vertical_queue.put(ipc_msg)
