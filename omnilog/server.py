# coding=utf-8

import http.server as Server
import threading
from omnilog.comm import Comm
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
            self.logger.info("SUB - " + self.name + " - Starting")

            address = (self.config['listenAddress'], self.config['listenPort'])
            self.request_handler.routes = self.routes
            httpd = Server.HTTPServer(address, self.request_handler)
            while self.runner.is_set():
                httpd.handle_request()
                self.logger.info("SUB - " + self.name + " - handling request ...")
        except KeyError:
            comm = Comm(self.name, Comm.ACTION_SHUTDOWN, "Config error detected.Shutting down.")
            self.vertical_queue.put(comm)

