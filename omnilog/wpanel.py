import json
import threading

from omnilog.server import HTTPServer


class WebPanel(threading.Thread):
    """
    This runnable has the responsibility or maintain the webpanel updated.
    It starts up the web server subsystem and forwards IPC signaling between the
    main process and the webserver.
    It consumes the web_panel_queue.
    """
    runner = None

    def __init__(self, runner, config, web_panel_queue):
        super().__init__()
        self.runner = runner
        self.config = config
        self.queue = web_panel_queue
        self.HTTP_server = HTTPServer
        self.data = {"config": self.config['frontEndConfig'], "logs": []}

    def run(self):

        web_server = self.HTTP_server(self.config['webServer'], self.runner)
        web_server.start()

        while self.runner.is_set():
            log = self.queue.get(True)

            if len(self.data['logs']) >= self.config['maxEntries']:
                self.data['logs'].pop()
            self.data['logs'].insert(0, log)
            with open(self.config['dataOutput'] + "/" + "logs.json", 'w') as f:
                json.dump(self.data, f, indent=4)
