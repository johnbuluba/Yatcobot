import unittest
from unittest.mock import patch, MagicMock

from tests.helper_func import load_fixture_config
from yatcobot.config import NotifiersConfig, Config
from yatcobot.plugins.notifiers import PushbulletNotifier, MailNotifier


class TestPushbulletNotifier(unittest.TestCase):

    def setUp(self):
        self.PushBullet = patch('yatcobot.plugins.notifiers.PushBullet').start()
        load_fixture_config()

    def tearDown(self):
        self.PushBullet.stop()

    def test_is_enabled_disabled(self):
        NotifiersConfig.get()['pushbullet']['enabled'] = False

        self.assertFalse(PushbulletNotifier.is_enabled())

    def test_is_enabled_enabled(self):
        NotifiersConfig.get()['pushbullet']['enabled'] = True

        self.assertTrue(PushbulletNotifier.is_enabled())

    def test_notify(self):
        NotifiersConfig.get()['pushbullet']['token'] = 'test'

        pushbullet_notifier = PushbulletNotifier()
        self.PushBullet.assert_called_once_with("test")

        pushbullet_notifier.notify("test", "test")

        self.PushBullet.return_value.push_note.assert_called_once_with("test", "test")

    def test_config(self):
        template = Config.get_template()
        self.assertIn(PushbulletNotifier.name, template['notifiers'])
        self.assertIn('enabled', template['notifiers'][PushbulletNotifier.name])
        self.assertIn('token', template['notifiers'][PushbulletNotifier.name])


class TestEmailNotifier(unittest.TestCase):

    def setUp(self):
        self.smtp = patch('yatcobot.plugins.notifiers.smtplib.SMTP').start()
        load_fixture_config()

    def tearDown(self):
        self.smtp.stop()

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

        mail_notifier = MailNotifier()

        mail_notifier.notify("test", "test")

        self.smtp.assert_called_once_with('test', 25)

        # TODO: More tests !

    def test_mail_test(self):
        mail_notifier = MailNotifier()
        mail_notifier.notify = MagicMock()

        mail_notifier.test()
        self.assertEqual(mail_notifier.notify.call_count, 1)

    def test_config(self):
        template = Config.get_template()
        self.assertIn(MailNotifier.name, template['notifiers'])
        self.assertIn('enabled', template['notifiers'][MailNotifier.name])
        self.assertIn('host', template['notifiers'][MailNotifier.name])
        self.assertIn('port', template['notifiers'][MailNotifier.name])
        self.assertIn('tls', template['notifiers'][MailNotifier.name])
        self.assertIn('username', template['notifiers'][MailNotifier.name])
        self.assertIn('password', template['notifiers'][MailNotifier.name])
        self.assertIn('recipient', template['notifiers'][MailNotifier.name])
