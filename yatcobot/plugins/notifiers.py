import logging
import smtplib
from abc import abstractmethod
from email.mime.text import MIMEText

import confuse
from pushbullet import PushBullet

from yatcobot.config import NotifiersConfig
from yatcobot.plugins import PluginABC

logger = logging.getLogger(__name__)


class NotifierABC(PluginABC):
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

    @staticmethod
    def get_enabled():
        """Retuns a list of instances of notifiers that are enabled"""
        enabled = list()
        for cls in NotifierABC.__subclasses__():
            if cls.is_enabled():
                enabled.append(cls())
        return enabled

    @staticmethod
    def get_config_template():
        """
        Creates the config template for all notifiers
        :return: config template
        """
        template = dict()
        for cls in NotifierABC.__subclasses__():
            template[cls.name] = cls.get_config_template()
        return template


class PushbulletNotifier(NotifierABC):
    name = 'pushbullet'

    def __init__(self):
        self.pb = PushBullet(NotifiersConfig.get().pushbullet.token)

    def notify(self, title, message):
        self.pb.push_note(title, message)

    @staticmethod
    def is_enabled():
        if NotifiersConfig.get().pushbullet.enabled:
            return True
        return False

    @staticmethod
    def get_config_template():
        template = {
            'enabled': confuse.TypeTemplate(bool),
            'token': confuse.String()
        }
        return template


class MailNotifier(NotifierABC):
    name = 'mail'

    def __init__(self):
        self.host = NotifiersConfig.get().mail.host
        self.port = NotifiersConfig.get().mail.port
        self.tls = NotifiersConfig.get().mail.tls
        self.username = NotifiersConfig.get().mail.username
        self.password = NotifiersConfig.get().mail.password
        self.recipient = NotifiersConfig.get().mail.recipient

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

    @staticmethod
    def get_config_template():
        template = {
            'enabled': confuse.TypeTemplate(bool),
            'host': confuse.String(),
            'port': confuse.Integer(),
            'tls': confuse.TypeTemplate(bool),
            'username': confuse.String(),
            'password': confuse.String(),
            'recipient': confuse.String()
        }
        return template
