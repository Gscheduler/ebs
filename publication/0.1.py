#!/usr/bin/env python
# coding=utf-8

import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor,ProcessPoolExecutor
import logging
import logging.handlers
from ConfigParser import ConfigParser,MissingSectionHeaderError
from socket import gethostname
import subprocess
import time

LOG_FILE = 'tst.log'

handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5)  # 实例化handler
fmt = '%(asctime)s - %(filename)s[line:%(lineno)d] - %(process)d - %(levelname)s - %(message)s'

formatter = logging.Formatter(fmt)  # 实例化formatter
handler.setFormatter(formatter)  # 为handler添加formatter

logger = logging.getLogger('tst')  # 获取名为tst的logger
logger.addHandler(handler)  # 为logger添加handler
logger.setLevel(logging.DEBUG)


conf_ini = "/Users/Corazon/PycharmProjects/untitled7/test1.ini"



def getstatusoutput(cmd):
    start = time.time()
    p = subprocess.Popen('%s' % cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    status = p.wait()
    end = time.time()
    exec_time = end - start
    stdout = p.stdout.readlines()
    pid = p.pid
    logger.debug("主机名:%s - 进程:%d - 返回值:%d - 执行时长:%0.2f/s - 命令:%s - 程序输出:%s" % (gethostname(),pid,status,exec_time,cmd,str(stdout)[0:20481]))
    return status,stdout


class TaskSched:

    def __init__(self):
        self._sched = BackgroundScheduler(max_instances=3,misfire_grace_time=180,coalesce=False)
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

    def task(self,cmd):
        getstatusoutput(cmd)

    def load_sched(self):
        job_list,job_len=self.parser_config(conf_ini)

        for num in range(job_len):
            job_info = job_list[num]
            for jobkey,jobvalue in job_info.items():
                arg_list = []
                result = self.check_jobs(''.join(jobvalue['cmd']))
                if result and len(jobvalue['sec']) == 1:
                    arg_list.append(jobvalue['cmd'])
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

    print 'Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ap_sched._sched.shutdown()