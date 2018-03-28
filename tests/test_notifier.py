import random
import unittest
from unittest.mock import patch, MagicMock

from yatcobot.notifier import NotificationService, PushbulletNotifier, AbstractNotifier


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

    @patch('yatcobot.notifier.Config')
    def test_is_enabled_disabled(self, Config):
        Config.pushbullet_token = ''

        self.assertFalse(PushbulletNotifier.is_enabled())

    @patch('yatcobot.notifier.Config')
    def test_is_enabled_enabled(self, Config):
        Config.pushbullet_token = 'test'

        self.assertTrue(PushbulletNotifier.is_enabled())

    @patch('yatcobot.notifier.Config')
    def test_notify(self, Config):
        Config.pushbullet_token = 'test'

        pushbullet_notifier = PushbulletNotifier.from_config()
        self.PushBullet.assert_called_once_with("test")

        pushbullet_notifier.notify("test", "test")

        self.PushBullet.return_value.push_note.assert_called_once_with("test", "test")
