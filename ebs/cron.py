p# coding:utf-8
from ConfigParser import ConfigParser, ParsingError
from datetime import datetime, timedelta
from urllib import unquote
import os, sys
import time
import socket
import json
import multiprocessing
import signal
import  atexit
#配置日志记录的基本信息
#import logging
#logging.basicConfig(filename='/tmp/apollocrond.log', filemode='a',
#        format='[%(asctime)s] %(message)s', level=logging.INFO)

#导入外部库
BIN_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BIN_DIR)
LIB_DIR = os.path.join(ROOT_DIR, 'Lib')
sys.path.insert(0, LIB_DIR)

import pyinotify
from apolloscheduler import ApolloScheduler
from apscheduler.triggers import CronTrigger
from apscheduler.events import *

from util import getHostname, getstatusoutput
from util.logger import log
from util.simplelog import SimpleLog
from conf import DEFAULT

queue = multiprocessing.Queue(100)

def parseCrontab(config):
    """
        purpose:解析apollo crontab的配置文件
        return:
    """
    new_cron_jobs = {}
    parser = ConfigParser()
    try:
        parser.read(config)
    except ParsingError, e:
        log.error(str(e))
        return new_cron_jobs, False
    if not len(parser.sections()):
        log.info('empty config file')
        time.sleep(0.05)
        parser.read(config)
        log.info('reload config file')
    hostname = getHostname()
    log.info(hostname)
    #conf_jobs = [(sec,dict(parser.items(sec))) for sec in parser.sections()]
    for sec in parser.sections():
        if not sec.isdigit():continue
        job = dict(parser.items(sec))
        if hostname in [name.strip() for name in job['hostlist'].split(',')]:
            fields = job['task_interval'].split()
            try:
                trigger = CronTrigger(minute=fields[0], hour=fields[1],
                                    day=fields[2], month=fields[3], day_of_week=fields[4])
            except Exception, e:
                log.error(e.message)
                continue
            #print trigger.get_next_fire_time(datetime.now())
            new_cron_jobs[sec] = {
                    'name'   : job['task_name'],
                    'args'   : [unquote(job['task_content']).strip(), sec],
                    'trigger': trigger
            }
    log.info(','.join(new_cron_jobs.keys()))
    return new_cron_jobs, True

class ApolloCrond(object):
    """ 任务调度类 """

    _linedelimiter = '\r\n'
    code_string = {
                EVENT_JOB_STARTED   :'任务开始执行...',
                EVENT_JOB_MISSED    :'任务错过调度时间,*未被调度*',
    }
    def __init__(self, mq, cronfile):
        if not os.path.exists(cronfile):
            sys.exit(111)
        self._mq = mq
        self._cronfile = cronfile
        self.host = getHostname()
        self.my_init()

    class UpdateConfig(pyinotify.ProcessEvent):
        """
        该类负责对inotify事件进行处理
        """
        def __init__(self, ap_crond):
            self._crond = ap_crond

        def process_IN_MODIFY(self, event):
            """
            当cron配置文件发生变化时作相应的更新
            """
            if os.path.realpath(os.path.abspath(self._crond._cronfile)) == event.pathname:
                log.info('crontab配置文件发生变化，重新载入, event:%s' % event.maskname)
                self._crond.refreshJobs()


        process_IN_MOVED_TO = process_IN_MODIFY

    def refreshJobs(self):
        """
        purpose:计划任务随配置的变化而变化
        """
        self.host = getHostname()
        start = time.time()
        cron_jobs, status = parseCrontab(self._cronfile)
        end = time.time()
        log.info('重新载入配置文件耗时:%fs' % (end - start))
        if status:
            running_jobs = self._ap_sched.get_jobs()
            new_jobs = set(cron_jobs.keys()) - set(running_jobs.keys())
            old_jobs = set(running_jobs.keys()) - set(cron_jobs.keys())
            samename_jobs = set(cron_jobs.keys()) & set(running_jobs.keys())
            for key in old_jobs:
                self._ap_sched.unschedule_job(running_jobs[key])
            for key in new_jobs:
                self._ap_sched.add_job(key, cron_jobs[key]['name'],
                                        cron_jobs[key]['trigger'], self.execCmd,
                                        args=cron_jobs[key]['args'], kwargs=None)
            for key in samename_jobs:
                trigger = None
                args = None
                new_name = None
                if str(cron_jobs[key]['trigger']) != str(running_jobs[key].trigger):
                    trigger = cron_jobs[key]['trigger']
                if cron_jobs[key]['args'] != running_jobs[key].args:
                    args = cron_jobs[key]['args']
                if cron_jobs[key]['name'] != running_jobs[key].name:
                    new_name = cron_jobs[key]['name']
                if trigger or args or new_name:
                    self._ap_sched.update_job(running_jobs[key], trigger, args, new_name)
                    log.info('job[%s] changed' % key)
            #log.info(self._ap_sched.get_jobs().keys())

    def my_init(self):
        """
        调度器的初始化以及crontab文件监控的初始化
        """
        options = {
            'threadpool.core_threads': 5,
            'threadpool.max_threads': 100,
            'misfire_grace_time': 300
        }
        ap_sched = ApolloScheduler(daemonic=False, **options)
        ap_sched.add_listener(self.dealJobEvent)
        cron_jobs, status = parseCrontab(self._cronfile)
        if not status:
            sys.exit(255)
        for jobkey, jobinfo in cron_jobs.iteritems():
            ap_sched.add_job(jobkey, jobinfo['name'], jobinfo['trigger'],
                                self.execCmd, args=jobinfo['args'], kwargs=None)
        self._ap_sched = ap_sched
        wm = pyinotify.WatchManager()
        notifier = pyinotify.ThreadedNotifier(wm, self.UpdateConfig(self))
        mask = pyinotify.IN_MODIFY|pyinotify.IN_MOVED_TO
        wm.add_watch(os.path.dirname(self._cronfile), mask, rec=False, auto_add=False)
        self._notifier = notifier

    def execCmd(self, cmd, ctid):
        """crontab 的实际执行过程"""
  oc      pscmd = "ps -A -opid,ppid,state,user,cmd|grep '\-\-ctid %s;'|grep -v 'grep '" % ctid
        rets, retv = getstatusoutput(pscmd)
        retv = retv.strip()
        log.info('ps 结果: \n%s' % retv)
        if retv:
            log.info('apollocrond重启后检测到任务[%s]还在执行' % cmd)
            return {'seq': -2,
                    'exec_time': 0,
                    'stats': 0,
                    'output': '检测到相同任务正在执行,*未被调度*',
                    }
        start = time.time()
        status, output = getstatusoutput(cmd)
        log.info('EXEC %s: %d' % (cmd, status))
        end = time.time()
        exec_time = end - start
        return {'seq': 3, 'exec_time': '%.3f' % exec_time, 'stats': status, 'output': output}

    def putmsg(self, msg):
        """
        将执行结果放入消息队里
        """
        try:
            self._mq.put_nowait(msg)
        except:
            pass


    def start(self):
        """
        启动调度器和配置文件监视器
        """
        log.info('apollocrond start')
        self._ap_sched.start()
        self._notifier.loop()

    def dealJobEvent(self, event):
        """
        处理调度过程中产生的事件
         - event : 事件的相关信息对象
        """

        def_ret = {
                    'jn'    : self._ap_sched._jobs_num,
                    'host_name'  : self.host,
                  }
        if EVENT_JOB_STARTED == event.code or EVENT_JOB_MISSED == event.code:
            log.info('[%s] %s, 任务数 %d' % (event.job.name, self.code_string[event.code], def_ret['jn']))
            ret = {
                    'cid'   : event.job.key,
                    'name'  : event.job.name,
                    'seq'   : 1 if EVENT_JOB_STARTED == event.code else -1,
                    'stats' : 0,
                    'exec_time' : 0,
                    'stime' : str(event.scheduled_run_time),
                    'output': self.code_string[event.code],
                  }
            ret.update(def_ret)
            info = {
                    'req_type': 'RESPONSE',
                    'res_type': 'CRON',
                    'retval'  : json.dumps(ret),
                   }
            self.putmsg(json.dumps(info))
        elif EVENT_JOB_EXECUTED == event.code:
            retval = event.retval
            if -2 == retval['seq']:
                log.info('[%s]已经在执行,不被调度' % event.job.name)
            else:
                log.info('[%s] 执行完成, 任务数 %d' % (event.job.name, def_ret['jn']))

            retval.update(def_ret)
            retval.update(name=event.job.name, cid = event.job.key, stime=str(event.scheduled_run_time))
            info = {
                    'req_type': 'RESPONSE',
                    'res_type': 'CRON',
                    'retval': json.dumps(retval),
                   }
            self.putmsg(json.dumps(info))
        elif EVENT_JOB_MAXINSTANCE == event.code:
            log.info('job[%s] reach max instance, 不被调度' % event.job.name)
        elif EVENT_JOBSTORE_JOB_ADDED == event.code:
            log.info('job[%s] added, 任务数 %d' % (event.job.name, def_ret['jn']))
        elif EVENT_JOBSTORE_JOB_REMOVED == event.code:
            log.info('job[%s] removed, 任务数 %d' % (event.job.name, def_ret['jn']))
        elif EVENT_JOB_ERROR == event.code:
            log.info('job[%s] error:%s' % (event.job.name,event.exception))


class MessageSender(object):
    def __init__(self, mq, address, logfile):
        self._mq = mq
        self._address = address
        self._logger = SimpleLog(logfile, 'cronworker', backcount=2)

    def createConnection(self):
        """创建到远程服务的链接直到成功为止,返回链接对象"""
        connection = None
        step = 5
        while 1:
            try:
                connection = socket.create_connection(self._address, timeout=1)
            except Exception, e:
                self._logger.error("连接到%s失败:%s" % (str(self._address), e.args[1]))
                self._logger.info("队列中消息数: %d" % self._mq.qsize())
                if self._mq.qsize()*1.0/self._mq._maxsize > 0.8:
                    break
                else:
                    time.sleep(step)
            else:
                self._logger.info("连接到%s成功" % str(self._address))
                break
        return connection

    def run(self):
        self._logger.info('cron sender started')
        delimiter = "\r\n"
        error = False
        conn = self.createConnection()
        count = 0
        msg = ""
        while 1:
            #没有发送错误时,从队列中取出信息
            if not error:
                msg = self._mq.get()
            #如果连接失败返回,说明队列里消息快满了,丢掉比较老的消息
            if conn is None:
                self._logger.error(msg)
                msg = self._mq.get()
                conn = self.createConnection()
                continue
            try:
                conn.sendall(msg + delimiter)
            except Exception, e:
                self._logger.error('send error: %s' % e.args[1])
                self._logger.info("队列中消息数: %d" % self._mq.qsize())
                conn.close()
                error = True
                cunnt = 0
                conn = self.createConnection()
            else:
                self._logger.info('send msg success')
                error = False
            count += 1
            if count > 10:
                time.sleep(1)

def sendWork(q, addr):
    sender = MessageSender(q, addr,
                    os.path.join(DEFAULT['log_dir'] ,'cronsender.log'))
    sender.run()

def cronWork(q, conf):
    ap_crond = ApolloCrond(q,conf)
    ap_crond.start()

if '__main__' == __name__:
    children = {}
    @atexit.register
    def noticeChildren():
        for pid, child in children:
            if child.is_alive():
                child.terminate()

    log.setOwn('apollocrond')
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
                      help='toggle debug model, print message to screen')
    try:
        (options, args) = parser.parse_args()
    except :
        parser.print_usage()
        sys.exit(2)
    if options.debug:
        from util.logger import log
        log.setDebug()

    tasksend = multipressing.Process(target=sendWork,
                                args=(queue, DEFAULT['server_listener']))
    ap_crond = multiprocessing.Process(target=cronWork,
                                args=(queue, DEFAULT['crontab']))
    tasksend.start()
    ap_crond.start()
    children[tasksend.pid] = tasksend
    children[ap_crond.pid] = ap_crond
    while 1:
        try:
            pid, exitcode = os.wait()
        except OSError, e:
            print e
            if e.args[0] == 10:
                exit(0)
        if exitcode != 0:
            #如过子进程异常退出,重启子进程
            proc = children[pid]
            del children[pid]
            worker = multiprocessing.Process(target=proc._target, args = proc._args)
            worker.start()
            children[worker.pid] = worker
        time.sleep(10)

