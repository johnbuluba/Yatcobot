import logging
from abc import ABCMeta, abstractmethod, abstractstaticmethod, abstractclassmethod

from pushbullet import PushBullet

from .config import TwitterConfig, NotifiersConfig

logger = logging.getLogger(__name__)


class NotificationService:

    def __init__(self):
        self.active_notifiers = []
        self._intialize_notifiers()

    def send_notification(self, title, message):
        """Sends a message to all enabled notifiers"""
        for notifier in self.active_notifiers:
            notifier.notify(title, message)

    def _intialize_notifiers(self):
        """Adds all enabled notifiers in the active_notifiers list"""
        for cls in AbstractNotifier.__subclasses__():
            if cls.is_enabled():
                self.active_notifiers.append(cls.from_config())

    def is_enabled(self):
        """Checks if any notifier is enabled"""

        if len(self.active_notifiers) > 0:
            return True
        return False


class AbstractNotifier(metaclass=ABCMeta):
    """
    Abstract class that all methods that want to notify the user must derive from
    """

    @abstractmethod
    def notify(self, title, message):
        """Sends the message to the user"""

    @staticmethod
    @abstractstaticmethod
    def is_enabled():
        """
        Returns if its enabled or not
        :return: Bool
        """

    @classmethod
    @abstractclassmethod
    def from_config(cls):
        """
        Instatiates a Notifier class using parameters from config
        :return:
        """


class PushbulletNotifier(AbstractNotifier):

    def __init__(self, api_key):
        self.pb = PushBullet(api_key)

    def notify(self, title, message):
        self.pb.push_note(title, message)

    @staticmethod
    def is_enabled():
        if NotifiersConfig.get().pushbullet.enabled:
            return True
        return False

    @classmethod
    def from_config(cls):
        return cls(NotifiersConfig.get().pushbullet.token)
