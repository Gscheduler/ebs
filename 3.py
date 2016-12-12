#!/usr/bin/env python
# coding=utf-8
import os
from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
# from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor,ProcessPoolExecutor
from apscheduler.events import *
from ConfigParser import ConfigParser,MissingSectionHeaderError
from socket import gethostname
import subprocess
import time
# import tmp
from tempfile import TemporaryFile

conf_ini = "/Users/Corazon/PycharmProjects/untitled7/test1.ini"

LISTENER_JOB = (EVENT_JOB_ADDED |
                EVENT_JOB_REMOVED |
                EVENT_JOB_MODIFIED |
                EVENT_JOB_EXECUTED |
                EVENT_JOB_ERROR |
                EVENT_JOB_MISSED)

JOB_DEFAULTS = {
    'misfire_grace_time': 1,
    'coalesce': False,
    'max_instances': 3
}
EXECUTORS = {
    'default': ThreadPoolExecutor(1),
    'processpool': ProcessPoolExecutor(4)
}

def getstatusoutput(cmd, maxoutput=20481):
    try:
        f = TemporaryFile(mode='w+')
        p = subprocess.Popen('%s' % cmd, shell=True, stdout=f, close_fds=True)
        sts = p.wait()
        f.seek(0, 2)
        total = f.tell()
        # 如果标准输出过大,截断
        if maxoutput >= 0 and total > maxoutput:
            f.seek(-maxoutput, 2)
            text = f.read().decode('utf8', 'ignore').encode('utf8')
        else:
            f.seek(0)
            text = f.read()

    finally:
        f.close()
    print sts, text
    with open('/tmp/crontab.log','a+') as log:
        p = subprocess.Popen('%s' % cmd,shell=True,stdout=log)






class TaskSched:

    def __init__(self):
        self._sched = BackgroundScheduler(executors=EXECUTORS, job_defaults=JOB_DEFAULTS, timezone='Asia/Shanghai')
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

    def task2(self,cmd):
        subprocess.Popen('%s' % cmd,shell=True,stdout=subprocess.PIPE)

    def task(self,cmd):
        start = time.time()
        # status, output = getstatusoutput(cmd)
        status, output = getstatusoutput(cmd)
        end = time.time()
        exec_time = end - start
        # return {'seq': 3, 'exec_time': '%.3f' % exec_time, 'stats': status, 'output': output}
        print status,output

    def load_sched(self):
        job_list,job_len=self.parser_config(conf_ini)
        for num in range(job_len):
            job_info = job_list[num]
            for jobkey,jobvalue in job_info.items():
                arg_list = []
                result = self.check_jobs(''.join(jobvalue['cmd']))
                if result and len(jobvalue['sec']) == 1:
                    arg_list.append(jobvalue['cmd'])
                    # self.add_task(self.task,'interval',arg_list,seconds=int(''.join(jobvalue['sec'])),id=jobkey, name=jobvalue['name'])
                    self.add_task(self.task,'interval',arg_list,seconds=int(''.join(jobvalue['sec'])),id=jobkey, name=jobvalue['name'])
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
    def add_task(self,fun,trig,arg,**kwargs):
        self._sched.add_job(fun,trig,arg,**kwargs)

if __name__ == '__main__':
    ap_sched = TaskSched()
    ap_sched.load_sched()
    ap_sched._sched.start()

    # try:
    while True:
        time.sleep(3)
        a = ap_sched._sched.get_jobs()
        print a
    # except KeyboardInterrupt:
    #     ap_sched._sched.shutdown()
