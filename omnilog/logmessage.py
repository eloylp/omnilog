# coding=utf-8


class LogMessage(object):
    """
    Comunication object fopr passing logs through subsystems.

    """

    def __init__(self, name, data, system_notifications, timestamp):
        self._name = name
        self._data = data
        self._timestamp = timestamp
        self._system_notifications = system_notifications

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def timestamp(self):
        return self._name

    @timestamp.setter
    def timestamp(self, timestamp):
        self._timestamp = timestamp

    @property
    def system_notifications(self):
        return self._system_notifications

    @system_notifications.setter
    def system_notifications(self, system_notifications):
        self._timestamp = system_notifications

    def get_object(self):
        obj = {}
        for k, v in self.__dict__.items():
            obj[k[1:]] = v
        return obj
