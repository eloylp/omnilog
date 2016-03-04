# coding=utf-8


class Comm(object):
    """
    Comunication object between subsystems and main process.

    """
    ACTION_SHUTDOWN = "SHUTDOWN"
    ACTION_REBOOT = "REBOOT"

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
        obj = {
            "subsystem": self._subsystem,
            "action": self._action,
            "message": self._message
        }
        log_message = ''
        for k, v in obj.items():
            log_message += k + "-" + v + " | "

        return log_message.rstrip(" | ")
