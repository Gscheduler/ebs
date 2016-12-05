#!/usr/bin/env python
# coding=utf-8
import os
from apscheduler.schedulers.background import BlockingScheduler
from ConfigParser import ConfigParser,MissingSectionHeaderError
from socket import gethostname
import subprocess



class TaskSched:

    def __init__(self):
        self.sched = BlockingScheduler()
        self.parser = ConfigParser()
        self.options = {}
        self.hostname = gethostname()


    def __repr__(self):
        return '<Program is %r>' % self.name


    def parser_config(self,config_path):
        try:
            self.parser.read(config_path)
        except MissingSectionHeaderError:
            raise SyntaxError("Initialiser contains no section headers")

        if not len(self.parser.sections()):
            print  "empty config file."

        for section in self.parser.sections():
            job = dict(self.parser.items(section))
            if self.hostname in [name.strip() for name in job['hostlist'].split(',')]:
                new_interval_jobs = {}
                new_interval_jobs[section] = {
                    'name': job['task_name'].strip(),
                    'cmd': job['task_content'].strip(),
                    'sec': job['task_interval'].split()
                }
                self.interval_jobs(section,new_interval_jobs)

    def interval_jobs(self,section,new_interval_jobs):
        cmd = new_interval_jobs[section]['cmd']
        check_job_cmd = self.check_jobs(cmd)
        if check_job_cmd != True:
            print cmd


    def cron_jobs(self,section,options):
        pass

    def check_jobs(self,job_name):
        ck_cmd = "ps aux | grep '%s' |grep -v grep" % job_name
        p = subprocess.Popen(ck_cmd,shell=True,stdout=subprocess.PIPE)
        is_exist = False
        if p.wait() == 0:
            val = p.stdout.read()
            if job_name  in val:
                is_exist = True
                return is_exist,job_name




if __name__ == '__main__':
     TaskSched().parser_config('/Users/Corazon/PycharmProjects/untitled7/test.ini')




