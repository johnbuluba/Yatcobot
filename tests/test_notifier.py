import random
import unittest
from unittest.mock import MagicMock, patch

from yatcobot.notifier import NotificationService


class TestNotificationService(unittest.TestCase):

    @patch("yatcobot.plugins.notifiers.NotifierABC.__subclasses__")
    def test_initialize(self, __subclasses__):
        subclasses = [MagicMock() for x in range(10)]
        for x in subclasses:
            x.is_enabled.return_value = random.choice([True, False])

        __subclasses__.return_value = subclasses

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

    @patch("yatcobot.plugins.notifiers.NotifierABC.__subclasses__")
    def test_is_enabled_enabled(self, __subclasses__):
        subclasses = [MagicMock() for x in range(10)]
        for x in subclasses:
            x.is_enabled.return_value = random.choice([True, False])

        __subclasses__.return_value = subclasses

        n = NotificationService()

        self.assertTrue(n.is_enabled())
