# coding=utf-8

import http.server as Server
import threading

from omnilog.strings import Strings
from omnilog.ipcactions import IPCActions
from omnilog.ipcmessage import IPCMessage
from omnilog.logger import Logger


class RequestHandler(Server.SimpleHTTPRequestHandler):
    """
    Class to implement document root in simple.http server
    """
    routes = None

    def translate_path(self, path):
        return_path = False
        for patt, rootDir in self.routes:
            if path.startswith(patt):
                return_path = rootDir + path
                break
        return return_path


class HTTPServer(threading.Thread):
    """
    Our HTTP server wrapper class.
    """
    name = "SUB-HTTPServer"
    runner = None

    def __init__(self, config, runner, vertical_queue):
        super().__init__()
        self.config = config
        self.request_handler = RequestHandler
        self.runner = runner
        self.logger = Logger()
        self.routes = [
            ("/", self.config['docRoot'])
        ]
        self.vertical_queue = vertical_queue

    def run(self):
        """
        Runner for http server, uses user defined config for server.

        """
        try:
            self.logger.info(self.name + " " + Strings.SUB_SYSTEM_START)

            address = (self.config['listenAddress'], self.config['listenPort'])
            self.request_handler.routes = self.routes
            httpd = Server.HTTPServer(address, self.request_handler)
            while self.runner.is_set():
                httpd.handle_request()
        except KeyError:
            comm = IPCMessage(self.name, IPCActions.ACTION_SHUTDOWN, Strings.CONFIG_ERROR)
            self.vertical_queue.put(comm)
