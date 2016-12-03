# coding=utf-8
"""
Demonstrates how to use the background scheduler to schedule a job that executes on 3 second
intervals.
"""

from datetime import datetime
import time
import os

from apscheduler.schedulers.background import BackgroundScheduler


def tick():
    print('Tick! The time is: %s' % datetime.now())


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    # scheduler.add_job(tick, 'interval', seconds=3)
    # scheduler.add_job(tick, 'date', run_date='2016-02-14 15:01:05')
    scheduler.add_job(tick, 'cron', day_of_week='6', second='*/5')
    scheduler.start()  # 这里的调度任务是独立的一个线程
    scheduler.
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)  # 其他任务是独立的线程执行
            print('sleep!')
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print('Exit The Job!')
