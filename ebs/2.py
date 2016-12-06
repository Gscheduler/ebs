from pymongo import MongoClient
from apscheduler.schedu
from apscheduler.executors.pool import ThreadPoolExecutor,ProcessPoolExecutor

def my_job():
    print 'hello world'


jobstores = SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')lers.blocking import BlockingScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.jobstores.memory import  MemoryJobStore

executors = ThreadPoolExecutor(10)


job_defaults =
    'max_instances':3


scheduler = BlockingScheduler(jobstores=jobstores,executors=executors,job_defaults=job_defaults)
scheduler.add_job(my_job,'interval',seconds=3)

scheduler.get_jobs()

#try:
#    scheduler.start()
#except SystemExit:
#    client.close()