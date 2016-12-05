
from apscheduler.schedulers.blocking import BlockingScheduler
from ConfigParser import ConfigParser



def parser_config():
    cf = ConfigParser()
    cf.read('/Users/Corazon/PycharmProjects/untitled7/test.ini')



def my_job():
    "/usr/bin /Users/Corazon/PycharmProjects/untitled7/echo.sh"


sched = BlockingScheduler()
sched.add_job(my_job, 'interval', seconds=5)
sched.start()
#parser_config()
