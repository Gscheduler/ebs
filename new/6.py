from apscheduler.schedulers.background import BlockingScheduler,BaseScheduler,BackgroundScheduler
import time
def mainjob():
    print("It works!")

def mainjob2():
    print("works!")

if __name__ == '__main__':
    sched = BlockingScheduler()
    sched2 = BackgroundScheduler(standalone=True)
    sched2.start()
    sched2.add_job(mainjob,'interval',seconds=3)

    while True:
        # input("Press enter to exit.")
        time.sleep(3)
        sched2.add_job(mainjob2,'interval',seconds=1)
        a = sched2.get_jobs()
        print a
        sched2.e
    sched2.shutdown()