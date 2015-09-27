from collections import namedtuple
import random
import sched
import time
import logging

logger = logging.getLogger(__name__)


#Task types
NormalTask = namedtuple('NormalTask', ['delay', 'priority', 'action'])
RandomTask = namedtuple('RandomTask', ['delay', 'delay_margin', 'priority', 'action'])


class PeriodicScheduler(sched.scheduler):
    """Schedules tasks to be called periodically"""



    def __init__(self, timefunc=time.time, delayfunc=time.sleep):
        # List of tasks that will be periodically be called
        self.tasks = []
        super().__init__(timefunc, delayfunc)

    def enter(self, delay, priority, action):
        """Inserts a new task in the scheduler. Tasks will be called regularly with period delay"""

        task = NormalTask(delay, priority, action)
        self.tasks.append(task)

    def enter_random(self, delay, delay_margin, priority, action):
        """
        Inserts a new random task in the scheduler. Tasks will be paused for random time
        from delay-delay_margin to delay+delay_margin
        """
        task = RandomTask(delay, delay_margin, priority, action)
        self.tasks.append(task)

    def run(self, blocking=True):
        for i in range(len(self.tasks)):
            self.run_task(i)

        super().run(blocking)

    def enter_task(self, index):
        task = self.tasks[index]
        if isinstance(task, NormalTask):
            super().enter(task.delay, task.priority, self.run_task, argument=(index,))

        elif isinstance(task, RandomTask):
            delay = random.randint(task.delay- task.delay_margin, task.delay + task.delay_margin)
            super().enter(delay, task.priority, self.run_task, argument=(index,))

    def run_task(self, index):
        self.enter_task(index)
        try:
            logger.debug("Scheduler is calling: {}".format(self.tasks[index].action.__name__))
            self.tasks[index].action()
        except Exception as e:
            logger.error("Exception in scheduled task :{}".format(e), exc_info=True)