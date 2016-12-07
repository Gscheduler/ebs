#!/usr/bin/env python
# coding=utf-8
import os
from apscheduler.schedulers.background import BlockingScheduler,BackgroundScheduler

from ConfigParser import ConfigParser,MissingSectionHeaderError
from socket import gethostname
import subprocess
import time
from  multiprocessing import Pool
import logging


conf_ini = "/Users/Corazon/PycharmProjects/untitled7/test1.ini"
class TaskSched:

    def __init__(self):
        self.sched = BackgroundScheduler()
        self.parser = ConfigParser()
        self.options = {}
        self.hostname = gethostname()


    def __repr__(self):
        return '<Program is %r>' % self.name


    def parser_config(self,config_path):
        try:
            self.parser.read(config_path)
        except MissingSectionHeaderError:
            raise SyntaxError("Initialiser contains no section headers.")

        if not len(self.parser.sections()):
            print  "Empty config file."

        for section in self.parser.sections():
            n = 0
            job = dict(self.parser.items(section))
            if self.hostname in [name.strip() for name in job['hostlist'].split(',')]:
                new_interval_jobs = {}
                new_interval_jobs[section] = {
                    'name': job['task_name'].strip(),
                    'cmd': job['task_content'].strip(),
                    'sec': job['task_interval']
                }
                print new_interval_jobs
                result = self.check_jobs(new_interval_jobs[section]['cmd'])
                if not result:
                    for jobkey,jobinfo in new_interval_jobs.items():
                        t_list = []
                        t_list.append(jobinfo['cmd'])
                        self.sched.add_job(self.task2,'interval',t_list,seconds=int(jobinfo['sec']),id=jobkey,name=jobinfo['name'])
                        print t_list
        self.sched.start()
        self.sched.get_jobs()
        try:
            while True:
                time.sleep(3)
                print "test"
        except Exception:
            pass


    def task2(self,cmd):
        task = "%s" % cmd
        return subprocess.Popen(task,shell=True,stdout=subprocess.PIPE)

   # def process_pool(self):
   #     self._pool.apply_async(self.block_sched(), args=(i,))
    def t(self):
        print "hello world"

    def add_sched(self):
        pass
    def check_jobs(self,job_name):
        ck_cmd = "ps aux | grep '%s' |grep -v grep" % job_name
        p = subprocess.Popen(ck_cmd,shell=True,stdout=subprocess.PIPE)
        is_exist = False
        if p.wait() == 0:
            val = p.stdout.read()
            if job_name  in val:
                is_exist = True
        return is_exist

if __name__ == '__main__':
     ap_sched = TaskSched()
     ap_sched.parser_config(conf_ini)
