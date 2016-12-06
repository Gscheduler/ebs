from apscheduler.schedulers.background import  BackgroundScheduler

sched = BackgroundScheduler()

def tick():
    print "text"
args = {
    'seconds' : 3

}
sched.add_job(tick,'interval',args=args,seconds=1)
sched.start()
try:
    while True:

        pass
except Exception:
    pass