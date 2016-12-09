#!/usr/bin/env python
# coding=utf-8
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor,ProcessPoolExecutor
from apscheduler.events import *
from ConfigParser import ConfigParser,MissingSectionHeaderError
from socket import gethostname
import subprocess
import time
import commands
from  multiprocessing import Pool

conf_ini = "/Users/Corazon/PycharmProjects/untitled7/test1.ini"
class TaskSched:

    def __init__(self):
        # self._sched = BackgroundScheduler(replace_existing=True)
        self.parser = ConfigParser()
        self._hostname = gethostname()
        self._job_list = []
        self._basedir = os.path.abspath(os.path.dirname(__file__))

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
            if self._hostname in [name.strip() for name in job['hostlist'].split(',')]:
                new_interval_jobs = {}
                new_interval_jobs[section] = {
                    'name': job['task_name'].strip(),
                    'cmd': job['task_content'].strip(),
                    'sec': job['task_interval'].split()
                }

                self._job_list.append(new_interval_jobs)
        return self._job_list,len(self._job_list)

    def task(self,cmd):
        task = "%s" % cmd
        return subprocess.Popen(task,shell=True,stdout=subprocess.PIPE)

    def add_sched(self):
        job_list,job_len=self.parser_config(conf_ini)
        for num in range(job_len):
            job_info = job_list[num]
            for jobkey,jobvalue in job_info.items():
                arg_list = []
                result = self.check_jobs(jobvalue['cmd'])
                if result and len(jobvalue['sec']) == 1:
                    arg_list.append(jobvalue['cmd'])
                    self._sched.add_job(self.task, 'interval', arg_list, seconds=int(''.join(jobvalue['sec'])),id=jobkey, name=jobvalue['name'])
                elif result and len(jobvalue['sec']) == 5:
                    pass

    def check_jobs(self,job_name):
        ck_cmd = "ps aux | grep '%s' |grep -v grep" % job_name
        p = subprocess.Popen(ck_cmd,shell=True,stdout=subprocess.PIPE)
        is_exist = True
        if p.wait() == 0:
            val = p.stdout.read()
            if job_name  in val:
                is_exist = False
        return is_exist
    #
    def sched_init(self):
        # jobstores = {
            # 'default': MemoryJobStore(),
            # 'sqlalchemy': SQLAlchemyJobStore(url="'sqlite:///' + os.path.join(basedir, 'data.sqlite'")
        # }
        executors = {
            'default': ThreadPoolExecutor(30),
            'processpool': ProcessPoolExecutor(12)
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        # sched = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
        sched = BackgroundScheduler(executors=executors, job_defaults=job_defaults)

        return sched


if __name__ == '__main__':
    ap_sched = TaskSched()
    ap_sched.add_sched()
    ap_sched._sched.start()
    try:
        while True:
            time.sleep(3)
            a = ap_sched._sched.get_job('4')
            b = ap_sched._sched.get_job('5')
            c = ap_sched._sched.get_job('6')
            print a
            print b
            print c

    except KeyboardInterrupt:
        ap_sched._sched.shutdown()




    #ap_sched.sched.start()

    # while True:
    #     try:
    #         time.sleep(1)
    #         pass
    #     except KeyboardInterrupt:
    #         ap_sched.sched.shutdown()

