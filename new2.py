import os
from apscheduler.schedulers.background import BlockingScheduler
from ConfigParser import ConfigParser

def cron_jobs():
    pass


class TaskSched:

    def __init__(self):
        self.sched = BlockingScheduler()
        self.parser = ConfigParser()
        self.para = {}
    ever_jobs()
def ever_jobs():
    pass
    che = ConfigParser()

def get_jobs(config):
    sched = BlockingScheduler()
    parser = ConfigParser()
    parser.read(config)
    for section in parser.sections():
        para.setdefault(section, []).append(parser.options(section))
        if para.get(section) >= 5:
            cron_jobs()
        else:
            ever_jobs()


if __name__ == '__main__':
    a = TaskSched()
    a.get_jobs('/usr/local/Cellar/python/2.7.11/bin/task.ini')





