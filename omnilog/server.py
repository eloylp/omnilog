import http.server as Server
import threading


class RequestHandler(Server.SimpleHTTPRequestHandler):
    routes = None

    def translate_path(self, path):
        returnPath = False
        for patt, rootDir in self.routes:
            if path.startswith(patt):
                returnPath = rootDir + path
                break
        return returnPath


class HTTPServer(threading.Thread):
    runner = None

    def __init__(self, config, runner):
        super().__init__()
        self.config = config
        self.request_handler = RequestHandler
        self.runner = runner
        self.routes = [
            ("/", self.config['docRoot'])
        ]

    def run(self):
        address = (self.config['listenAddress'], self.config['listenPort'])
        self.request_handler.routes = self.routes
        httpd = Server.HTTPServer(address, self.request_handler)
        while self.runner.is_set():
            httpd.handle_request()

