import notify2

from omnilog.strings import Strings


class Notifier(object):
    """
    Wrapper for the notify2 library.
    """

    def __init__(self):
        self.appName = Strings.APP_NAME
        notify2.init(self.appName)

    def send_notify(self, title, body):
        n = notify2.Notification(
            title,
            body
        )
        n.show()
