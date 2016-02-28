import notify2


class Notifier(object):
    def __init__(self):
        self.appName = "omnilog"
        notify2.init(self.appName)

    def send_notify(self, title, body):
        n = notify2.Notification(
            title,
            body
        )
        n.show()
