#!/usr/bin/env python
# coding=utf-8
import os
from apscheduler.schedulers.background import BlockingScheduler
from ConfigParser import ConfigParser

class TaskSched:

    def __init__(self):
        self.sched = BlockingScheduler()
        self.parser = ConfigParser()
        self.options = {}

    def __repr__(self):
        return '<Program is %r>' % self.name

    # 读取配置ini文件生成配置段.添加字典key为选项,value为列表格式.
    # 判断配置选项如果大于5项,则为cron任务配置,否则为长期执行任务.
    def read_config(self,config_path):
        self.parser.read(config_path)
        for section in self.parser.sections():
            self.options.setdefault(section, []).append(self.parser.options(section))
            options_values = self.options.get(section)[0]
            if len(options_values) >= 3:
                self.cron_jobs(section,options_values)
            else:
                self.invercal_jobs(section,options_values)


    def invercal_jobs(self,section,options):
        options_
        print section
        task_name = self.parser.get(section,options[0])
        task_contect = self.parser.get(section,options[1])
        task_contect_show = self.parser.get(section,options[2])
        print  self.parser.get(section,options[0])

    def cron_jobs(self,section,options):
        task_num = section
        task_name = self.parser.get(section,options[0])
        task_contect = self.parser.get(section,options[1])
        task_contect_show = self.parser.get(section,options[2])
        #print  self.parser.get(section,options[3])
        print task_num




#    def cron_option_para(self,slice):
#        return {'0':'task_name','1':'task_contect','2':'task_contect_show','3':'invercal','4':'sudo_user'}


if __name__ == '__main__':
     TaskSched().read_config('/usr/local/Cellar/python/2.7.11/bin/task.ini')
from apscheduler.triggers.base import BaseTrigger





