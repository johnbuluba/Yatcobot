import builtins
import unittest
from unittest.mock import patch, mock_open, Mock

from main import Config, PeriodicScheduler


class TestConfig(unittest.TestCase):

    config_data='''{"search-queries":["test"],"follow-keywords":["test"],"fav-keywords":["test"],"scan-update-time":1,"retweet-update-time":1,"rate-limit-update-time":1,"min-ratelimit":1,"min-ratelimit-retweet":1,"min-ratelimit-search":1,"clear-queue-time":1,"min-posts-queue":1,"blocked-users-update-time":1,"max-follows":1,"consumer-key":"test","consumer-secret":"test","access-token-key":"test","access-token-secret":"test"}'''

    def test_load(self):

        #Mock open to return the confi_data from file
        with patch.object(builtins,'open',mock_open(read_data=self.config_data)) as m:
            Config.load("test")

        self.assertEqual(Config.search_queries, ["test"])
        self.assertEqual(Config.follow_keywords,["test"])
        self.assertEqual(Config.scan_update_time, 1)
        self.assertEqual(Config.retweet_update_time, 1)
        self.assertEqual(Config.rate_limit_update_time, 1)
        self.assertEqual(Config.min_ratelimit, 1)
        self.assertEqual(Config.min_ratelimit_search, 1)
        self.assertEqual(Config.clear_queue_time, 1)
        self.assertEqual(Config.min_posts_queue, 1)
        self.assertEqual(Config.blocked_users_update_time, 1)
        self.assertEqual(Config.max_follows, 1)
        self.assertEqual(Config.consumer_key, "test")
        self.assertEqual(Config.consumer_secret, "test")
        self.assertEqual(Config.access_token_key, "test")
        self.assertEqual(Config.access_token_secret, "test")


class TestPeriodicScheduler(unittest.TestCase):
    """Tests for PeriodicScheduler class"""

    def setUp(self):

        def time():
            #time.current_time += 1
            return time.current_time

        time.current_time = 0
        self.time = time
        self.sleep = Mock(return_value=0)
        self.sched = PeriodicScheduler(self.time, self.sleep)

    def test_enter(self):
        target = Mock(name='Test')

        #Add one task
        self.sched.enter(10, 1, target)
        self.assertEqual(len(self.sched.tasks), 1)
        self.assertEqual(self.sched.tasks[0], (10, 1, target))

        #Add a second task
        self.sched.enter(10, 1, target)
        self.assertEqual(len(self.sched.tasks), 2)
        self.assertEqual(self.sched.tasks[1], (10, 1, target))

    def test_enter_task(self):
        target = Mock(name='Test')

        #Add one task
        self.sched.enter(10, 1, target)

        self.sched.enter_task(0)

        self.assertEqual(len(self.sched.queue), 1)
        self.assertEqual(tuple(self.sched.queue[0]), (self.time.current_time+10, 1, self.sched.run_task, (0,), {}))

    def test_run_task(self):
        target = Mock(name='Test')
        target.__name__ = 'Test'

        #Add one task
        self.sched.enter(10, 1, target)
        self.sched.enter_task(0)

        #check time that is scheduled
        scheduled_time = self.sched.queue[0].time
        #Remove from queu (emulate that its called from the scheduler)
        self.sched._queue.pop()
        #Advance time
        self.time.current_time += 20

        #Run task
        self.sched.run_task(0)

        #Check that its called
        self.assertEqual(target.call_count, 1)

        #Check that its rescheduled
        self.assertEqual(len(self.sched._queue), 1)
        self.assertNotEqual(self.sched.queue[0].time, scheduled_time)
        self.assertEqual(tuple(self.sched.queue[0]), (self.time.current_time+10, 1, self.sched.run_task, (0,), {}))

    def test_run(self):

        targets = list()
        for i in range(10):
            target = Mock(name='Test')
            target.__name__ = 'Test'
            targets.append(target)

        for t in targets:
            self.sched.enter(10, 1, t)

        #advance clock
        self.time.current_time += 10

        self.sched.run(blocking=False)

        # Test if all targets run
        for t in targets:
            self.assertEqual(t.call_count, 1)

        # Test if rescheduled
        self.assertEqual(len(self.sched.queue), 10)
        for i in range(10):
            self.assertEqual(self.sched.queue[i].time, 20)

    def test_exception_in_target(self):

        def exception_target():
            raise Exception("test")

        #Add one task
        self.sched.enter(10, 1, exception_target)
        self.sched.enter_task(0)

        #Run task
        self.sched.run_task(0)


if __name__ == '__main__':
    unittest.main()