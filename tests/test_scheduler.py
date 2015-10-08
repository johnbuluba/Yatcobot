import os
import unittest
from unittest.mock import Mock
import logging

from yatcobot.scheduler import PeriodicScheduler

logging.disable(logging.ERROR)


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
        target.__name__ = 'Test'
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
        target.__name__ = 'Test'

        #Add one task
        self.sched.enter(10, 1, target)

        self.sched.enter_task(0)

        self.assertEqual(len(self.sched.queue), 1)
        self.assertEqual(tuple(self.sched.queue[0]), (self.time.current_time+10, 1, self.sched.run_task, (0,), {}))

    def test_enter_task_random(self):
        target = Mock(name='Test')
        target.__name__ = 'Test'

        #Add one task
        self.sched.enter_random(10, 5, 1, target)

        self.sched.enter_task(0)

        self.assertEqual(len(self.sched.queue), 1)
        self.assertGreaterEqual(self.sched.queue[0].time, self.time.current_time+10-5)
        self.assertLessEqual(self.sched.queue[0].time, self.time.current_time+10+5)
        self.assertEqual(self.sched.queue[0].action, self.sched.run_task)

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
        self.sched.run_task(0)
        self.sched.run_task(0)
        self.sched.run_task(0)


