# coding=utf-8


class Config(object):

    """
    This class object serves the configuration readed in the json file to all threads.
    Here there is no concurrency control, we dont need it.
    When the config watcher detects configuration changes in config.json, it firstly stops
    all threads / sub components. After this config object is done, The main module will
    startup all the threads again.
    """

    config_dict = None
