# coding=utf-8

import hashlib
import json
import threading
import time

from omnilog.config import Config
from omnilog.logger import Logger


class ConfigWatcher(threading.Thread):
    """
    App submodule. This runnable has the responsibility of read the
    json settings file, save hash information about it in memory and reload
    it if hash differs at some point of program execution.

    """
    runner = None
    name = "ConfigWatcher"

    def __init__(self, config_path, runner, vertical_queue):
        super().__init__()

        self.runner = runner
        self.vertical_queue = vertical_queue
        self.logger = Logger()
        self.interval_secs = 1
        self.config_path = config_path
        self.last_config_checksum = None

    def set_config(self):

        """
        Sets the parsed config into app config in memory object.

        """
        config_file = open(self.config_path)
        Config.config_dict = json.load(config_file)

    def run(self):

        """
        Endless loop execution.
        """
        counter = 0
        self.logger.info("SUB - " + self.name + " - Starting ")

        while self.runner.is_set():

            time.sleep(self.interval_secs)
            self.logger.info("SUB - " + self.name + " - Init config review ...")
            hash = hashlib.md5(open(self.config_path, 'rb').read()).hexdigest()
            if hash != self.last_config_checksum:
                self.set_config()
                self.last_config_checksum = hash
                if counter != 0:
                    self.vertical_queue.put("RESTART")
                    self.logger.info("SUB - " + self.name + " - Config changes detected ... setting new config.")
            counter += 1
