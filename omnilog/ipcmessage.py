# coding=utf-8


class IPCMessage(object):
    """
    Comunication object between subsystems and main process.

    """

    def __init__(self, subsystem, action, message):
        self._subsystem = subsystem
        self._action = action
        self._message = message

    @property
    def subsystem(self):
        return self._subsystem

    @subsystem.setter
    def subsystem(self, subsystem):
        self._subsystem = subsystem

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, action):
        self._action = action

    @property
    def message(self):
        return self._subsystem

    @message.setter
    def message(self, message):
        self._message = message

    def __str__(self):
        lm = []
        str = "{key} - {value}"
        for k, v in self.__dict__.items():
            lm.append(str.format(key=k[1:], value=v))

        return ' | '.join(lm)
