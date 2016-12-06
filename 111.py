#!/usr/bin/env python
# coding=utf-8
import os
from apscheduler.schedulers.background import BlockingScheduler,BackgroundScheduler
from ConfigParser import ConfigParser,MissingSectionHeaderError
from socket import gethostname
import subprocess
from  multiprocessing import Pool


class TaskSched:

    def __init__(self):
        #self.sched = BlockingScheduler()
        self.parser = ConfigParser()
        self.options = {}
        self.hostname = gethostname()
        self._pool = Pool(4)


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
            job = dict(self.parser.items(section))
            if self.hostname in [name.strip() for name in job['hostlist'].split(',')]:
                new_interval_jobs = {}
                new_interval_jobs[section] = {
                    'name': job['task_name'].strip(),
                    'cmd': job['task_content'].strip(),
                    'sec': job['task_interval']
                }
                self.interval_jobs(new_interval_jobs)


    def task2(self,):
        print "hello world"
        #cmd = "%s" % self.a
        #subprocess.Popen(cmd,shell=True)

    def interval_jobs(self,new_interval_jobs):
        for job_key,job_value in new_interval_jobs.items():
            job_value_cmd = self.check_jobs(job_value['cmd'])
            if job_value_cmd != True:
                #print job_value['cmd']
                self.a = job_value['cmd']
               # self.block_sched(job_value['sec'])
                #continue

   # def process_pool(self):
   #     self._pool.apply_async(self.block_sched(), args=(i,))

    def check_jobs(self,job_name):
        ck_cmd = "ps aux | grep '%s' |grep -v grep" % job_name
        p = subprocess.Popen(ck_cmd,shell=True,stdout=subprocess.PIPE)
        is_exist = False
        if p.wait() == 0:
            val = p.stdout.read()
            if job_name  in val:
                is_exist = True
                return is_exist

   # def block_sched(self,sec):
   #     s = int(sec)
   #     sched = BackgroundScheduler()
   #     sched.add_job(self.task2,'interval',seconds=1)
   #     sched.start()

            #print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

        #self.sched.get_jobs()
        #self.sched.shutdown()
        #pass

    #def task(self):
    #    print "hello world"


def task2():
    print "hello world"

if __name__ == '__main__':
     #TaskSched().parser_config('/Users/Corazon/PycharmProjects/untitled7/test.ini')
     sched = BackgroundScheduler()
     sched.add_job(task2,'interval',seconds=3)
     sched.start()