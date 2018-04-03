import random
import unittest
from unittest.mock import patch, MagicMock

from tests.helper_func import load_fixture_config
from yatcobot.config import NotifiersConfig
from yatcobot.notifier import NotificationService, PushbulletNotifier, AbstractNotifier, MailNotifier


class TestNotificationService(unittest.TestCase):

    def setUp(self):
        self.PushBullet = patch('yatcobot.notifier.PushBullet').start()

    def test_initialize(self):
        subclasses = [MagicMock() for x in range(10)]
        for x in subclasses:
            x.is_enabled.return_value = random.choice([True, False])

        AbstractNotifier.__subclasses__ = MagicMock()
        AbstractNotifier.__subclasses__.return_value = subclasses

        n = NotificationService()

        self.assertEqual(len(n.active_notifiers), len([x for x in subclasses if x.is_enabled.return_value]))

    def test_send_notification(self):
        n = NotificationService()
        # delete if some notifier is actualy loaded
        n.active_notifiers = []
        for i in range(10):
            n.active_notifiers.append(MagicMock())

        n.send_notification('test', 'test')

        for x in n.active_notifiers:
            x.notify.assert_called_once_with("test", "test")

    def test_is_enabled_disabled(self):
        n = NotificationService()
        # delete if some notifier is actualy loaded
        n.active_notifiers = []

        self.assertFalse(n.is_enabled())

    def test_is_enabled_enabled(self):
        subclasses = [MagicMock() for x in range(10)]
        for x in subclasses:
            x.is_enabled.return_value = random.choice([True, False])

        AbstractNotifier.__subclasses__ = MagicMock()
        AbstractNotifier.__subclasses__.return_value = subclasses

        n = NotificationService()

        self.assertTrue(n.is_enabled())


class TestPushbulletNotifier(unittest.TestCase):

    def setUp(self):
        self.PushBullet = patch('yatcobot.notifier.PushBullet').start()
        load_fixture_config()

    def test_is_enabled_disabled(self):
        NotifiersConfig.get()['pushbullet']['enabled'] = False

        self.assertFalse(PushbulletNotifier.is_enabled())

    def test_is_enabled_enabled(self):
        NotifiersConfig.get()['pushbullet']['enabled'] = True

        self.assertTrue(PushbulletNotifier.is_enabled())

    def test_notify(self):
        NotifiersConfig.get()['pushbullet']['token'] = 'test'

        pushbullet_notifier = PushbulletNotifier.from_config()
        self.PushBullet.assert_called_once_with("test")

        pushbullet_notifier.notify("test", "test")

        self.PushBullet.return_value.push_note.assert_called_once_with("test", "test")


class TestEmailNotifier(unittest.TestCase):

    def setUp(self):
        self.smtp = patch('yatcobot.notifier.smtplib.SMTP').start()
        load_fixture_config()

    def test_is_enabled_disabled(self):
        NotifiersConfig.get()['mail']['enabled'] = False

        self.assertFalse(MailNotifier.is_enabled())

    def test_is_enabled_enabled(self):
        NotifiersConfig.get()['mail']['enabled'] = True

        self.assertTrue(MailNotifier.is_enabled())

    def test_notify(self):
        NotifiersConfig.get()['mail']['enabled'] = True
        NotifiersConfig.get()['mail']['host'] = 'test'
        NotifiersConfig.get()['mail']['port'] = 25
        NotifiersConfig.get()['mail']['tls'] = True
        NotifiersConfig.get()['mail']['username'] = 'test@test.com'
        NotifiersConfig.get()['mail']['password'] = '123456'
        NotifiersConfig.get()['mail']['recipient'] = 'test@test.com'

        mail_notifier = MailNotifier.from_config()

        mail_notifier.notify("test", "test")

        self.smtp.assert_called_once_with('test', 25)

        # TODO: More tests !

    def test_mail_test(self):
        mail_notifier = MailNotifier.from_config()
        mail_notifier.notify = MagicMock()

        mail_notifier.test()
        self.assertEqual(mail_notifier.notify.call_count, 1)
