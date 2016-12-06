# coding=utf-8
"""
Demonstrates how to use the background scheduler to schedule a job that executes on 3 second
intervals.
"""

from datetime import datetime
import time
import os
import subprocess

from apscheduler.schedulers.background import BackgroundScheduler

def tick():
    print('1Tick! The time is: %s' % datetime.now())

def tick2():
    print('2Tick! The time is: %s' % datetime.now())

def tick3():
    print('3Tick! The time is: %s' % datetime.now())

def tick1(**kwargs):
    #print t1
    command = "%s" % f1
    #print type(command)
    return  subprocess.Popen(command,shell=True,stdout=subprocess.PIPE)



f1 = '/bin/bash /Users/Corazon/PycharmProjects/untitled7/echo.sh'



if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    #print t

    scheduler.add_job(tick1, 'interval', seconds=3) #间隔3秒钟执行一次
    scheduler.add_job(tick2, 'interval', seconds=4)  # 间隔3秒钟执行一次
    scheduler.add_job(tick3, 'interval', seconds=5)  # 间隔3秒钟执行一次
    scheduler.start()    #这里的调度任务是独立的一个线程

    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
try:
    # This is here to simulate application activity (which keeps the main thread alive).
    #n = 0
    while True:
        pass
        #time.sleep(2)  # 其他任务是独立的线程执行
        #print('sleep!')
        #n += 1
except (KeyboardInterrupt, SystemExit):
    # Not strictly necessary if daemonic mode is enabled but should be done if possible
    scheduler.shutdown()
    print('Exit The Job!')