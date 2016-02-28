import notify2


class Notifier(object):
    """
    Wrapper for the notify2 library.
    """

    def __init__(self):
        self.appName = "omnilog"
        notify2.init(self.appName)

    def send_notify(self, title, body):
        n = notify2.Notification(
            title,
            body
        )
        n.show()
