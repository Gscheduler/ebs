
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler,BlockingScheduler
from ConfigParser import ConfigParser
#from jobs import *

import
config_file = '/Users/Corazon/PycharmProjects/untitled7/test1.ini'

def tick(cmd):
    command = "ps aux | grep '%s' |grep -v grep" % cmd
    return subprocess.Popen(command,shell=True,stdout=subprocess.PIPE)

if __name__ == '__main__':
    parser = ConfigParser()
    parser.read(config_file)
    #sched = Scheduler(daemonic = False)
    #sched = BackgroundScheduler()
    sched = BlockingScheduler()

    for section in parser.sections():
        para = {}
        for (key, value) in parser.items(section):
            para[key] = value
         #   print para['task_name'

        a =para['task_content']
        b = lambda :a
        sched.add_job(b, 'interval',seconds=int(para['task_interval']))
    try:
        sched.start()
        print "*"
    except KeyboardInterrupt:
        sched.get_jobs()