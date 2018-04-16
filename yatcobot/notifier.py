import logging

from yatcobot.plugins.notifiers import NotifierABC

logger = logging.getLogger(__name__)


class NotificationService:

    def __init__(self):
        self.active_notifiers = NotifierABC.get_enabled()

    def send_notification(self, title, message):
        """Sends a message to all enabled notifiers"""
        for notifier in self.active_notifiers:
            notifier.notify(title, message)

    def is_enabled(self):
        """Checks if any notifier is enabled"""

        if len(self.active_notifiers) > 0:
            return True
        return False
