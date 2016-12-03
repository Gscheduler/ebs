from apscheduler.schedulers.blocking import  BlockingScheduler
def my_job():
    print 'Hello World'

sched = BlockingScheduler()
sched.add_job(my_job,'interval',seconds=5)
sched.start()