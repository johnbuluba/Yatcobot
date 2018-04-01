import logging
import smtplib
from email.mime.text import MIMEText
from abc import ABCMeta, abstractmethod

from pushbullet import PushBullet

from .config import NotifiersConfig

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
    @abstractmethod
    def is_enabled():
        """
        Returns if its enabled or not
        :return: Bool
        """

    @classmethod
    @abstractmethod
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


class MailNotifier(AbstractNotifier):

    def __init__(self, host, port, tls, username, password, recipient):
        self.host = host
        self.port = port
        self.tls = tls
        self.username = username
        self.password = password
        self.recipient = recipient

    def notify(self, title, message):
        msg = MIMEText(message)
        msg['Subject'] = title
        msg['From'] = self.username
        msg['To'] = self.recipient

        with smtplib.SMTP(self.host, self.port) as server:
            if self.tls:
                server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            logger.info('Email Notifier: sent notification to {}'.format(self.recipient))

    def test(self):
        """
        Method to send a test email
        """
        self.notify('Yatcobot', 'If you see this, email services works!')

    @staticmethod
    def is_enabled():
        if NotifiersConfig.get().mail.enabled:
            return True
        return False

    @classmethod
    def from_config(cls):
        return cls(NotifiersConfig.get().mail.host,
                   NotifiersConfig.get().mail.port,
                   NotifiersConfig.get().mail.tls,
                   NotifiersConfig.get().mail.username,
                   NotifiersConfig.get().mail.password,
                   NotifiersConfig.get().mail.recipient,
                   )
