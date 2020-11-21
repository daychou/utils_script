#!/usr/bin/env python
#coding=utf-8

import os
import time
import datetime
import shutil
import tarfile
import re
import argparse
import socket
import json
import requests
import operator
import logging
import subprocess


class logHandle(object):
    def __init__(self, rules, day=1):
        self.rules = rules
        self.day = day
        logging.basicConfig(filename='/tmp/log_clear.log',
                            level=logging.INFO,
                            format=
                            '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                            )

    def rever_date_list(self, date_list):
        '''
        指定N天前的日期集合列表，用于归档匹配日期清单
        :param date_list: 日志所包含的日期列表
        :return: 返回N天前以外的日期列表
        '''
        now_time = datetime.datetime.now()
        _date_list = []
        _rever_date_list = []
        if int(self.day) == 0:
            change_time = now_time + datetime.timedelta(days=+1)
            change_time = change_time.strftime('%Y-%m-%d')
            _date_list.append(change_time)
        else:
            for i in range(int(self.day)):
                change_time = now_time + datetime.timedelta(days=-i)
                change_time = change_time.strftime('%Y-%m-%d')
                _date_list.append(change_time)
        for date in date_list:
            if '-' not in date and len(date) == 8:
                date = date[:4] + '-' + date[4:6] + '-' + date[6:8]
                if date not in _date_list:
                    date = date.replace('-','')
                    _rever_date_list.append(date)
            else:
                if date not in _date_list:
                    _rever_date_list.append(date)
        return _rever_date_list

    def keyword_list(self, files):
        '''
        过滤文件符合正则表达式的字段并写入一个列表
        :param files:文件列表
        :return: 关键字列表
        '''
        _date_list = []
        for file in files:
            for rule in self.rules:
                pattern = re.compile(rule)
                log_date = re.findall(pattern, file)
                for _log_date in log_date:
                    _log_date = _log_date.strip("-")
                    if _log_date not in _date_list:
                        _date_list.append(_log_date)
        return _date_list

    def file_list(self, Logdir):
        '''
        根据目录返回该目录下的文件名列表
        :param Logdir: 目录位置
        :return: 返回文件名列表
        '''
        files = []
        for filename in os.listdir(Logdir):
            if filename.endswith('.log'):
                files.append(filename)
        return files

    def filter_list(self, files, condition=None):
        '''
        过滤日志文件
        :param files:文件列表
        :param condition: 匹配规则
        :return: 过滤包含.log和指定字符串的文件列表
        '''
        _files = []
        for file in files:
            if condition in file and file.endswith('.log'):
                _files.append(file)
        return _files

    def file_dir(self, dir, files, date):
        '''
        把指定文件归档到指定目录
        :param dir: 目录
        :param files: 文件列表
        :param date: 指定日期
        :return: 返回归档目录路径
        '''
        for num in range(100):
            _dir = dir + date + '.' + str(num) + '/'
            _tar_file = dir + date + '.' + str(num) + '.tar.gz'
            if os.path.isfile(_tar_file):
                continue
            else:
                os.mkdir(_dir)
                break
        if isinstance(files, list):
            for file in files:
                if os.path.exists('{0}{1}'.format(dir, file)):
                    shutil.move('{0}{1}'.format(dir, file), '{0}{1}'.format(_dir, file))
        return _dir

    def dir_tar(self, fileDir):
        '''
        压缩目录
        :param dir: 目录位置
        :return: 压缩后的文件路径
        '''
        if fileDir.endswith('/'):
            filename = fileDir.split('/')[-2]
            fileDir = os.path.dirname(os.path.dirname(fileDir))
        else:
            filename = fileDir.split('/')[-1]
            fileDir = os.path.dirname(fileDir)
        tar_filename = fileDir + '/' + filename + '.tar.gz'
        tar = tarfile.open(tar_filename, "w:gz")
        os.chdir(fileDir)
        tar.add(filename+'/')
        tar.close()
        if fileDir and filename:
            shutil.rmtree(fileDir + '/' + filename)
        return tar_filename

    def del_tar(self, day, logdir):
        '''
        删除N天前的日志
        :param day: 指定几天前
        :param Logdir: 指定需要删除的日志目录
        '''
        now_time = datetime.datetime.now()
        time_l = []
        for i in range(day):
            change_time = now_time + datetime.timedelta(days=-i)
            change_time = change_time.strftime('%Y-%m-%d')
            time_l.append(str(change_time))
        for filename in os.listdir(logdir):
            if filename.endswith('.tar.gz'):
                for rule in self.rules:
                    pattern = re.compile(rule)
                    log_date = re.findall(pattern, filename)
                    for _log_date in log_date:
                        if _log_date not in time_l:
                            os.remove(logdir + filename)
        return True

    def send_to_rebot(self, context, ddurl):
        '''
        发送通知到钉钉群
        '''
        data = json.dumps({"actionCard": {
            "title": "删除日志计划",
            "text": context,
            "hideAvatar": "0",
            "btnOrientation": "0",
            "btns": [
                {
                    "title": "通知消息",
                    "actionURL": "http://ops.hupu.io/domain/"
                }
            ]
        },
            "msgtype": "actionCard"
        })
        header = {'Content-Type': 'application/json; charset=utf-8'}
        requests.post(ddurl, data=data, headers=header)

    def del_log(self, logdir, files, logDateTime):
        '''
        删除files里2小时前修改的日志
        '''
        for logDate in logDateTime:
            for file in files:
                if logDate in file:
                    logmtime = int(os.stat(logdir + file).st_mtime)
                    localtime = int(time.time())
                    fsize = os.path.getsize(logdir + file)/1024/1024/1024
                    if operator.ge(fsize,2) and localtime-logmtime > 600:
                        os.remove(logdir + file)
                    elif localtime-logmtime > 7200:
                        os.remove(logdir + file)

    def empty_log(self, logdir, files, keyword_list):
        '''
        清空大于2G的日志
        '''
        fileTotalSize = 0
        fileList = []
        file2glist = []
        for keyword in keyword_list:
            for file in files:
                if keyword in file:
                    fsize = os.path.getsize(logdir + file)/1024/1024
                    if operator.ge(fsize,2048):
                        file2glist.append(logdir + file)
                    fileTotalSize = fileTotalSize + fsize
                    fileList.append(logdir + file)
        if operator.ge(fileTotalSize,20480):
            for logfile in fileList:
                with open(logfile, 'r+') as f:
                    f.truncate()
        else:
            for logfile in file2glist:
                with open(logfile, 'r+') as f:
                    f.truncate()

    def runCmd(self, cmd):
        '''
        :param cmd: shell
        :return: string int
        '''
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        except:
            logging.warning('{0} error'.format(cmd))
            return False, p.returncode
        else:
            output, err = p.communicate()
            if p.returncode != 0:
                logging.warning('{0} error: {1}'.format(cmd, err))
                return False, p.returncode
            logging.info('{0} success'.format(cmd))
        return output, p.returncode

def getAppname():
    '''
    获取主机名
    '''
    hostName = socket.gethostname()
    hostnames = hostName.split('-')
    if hostName.endswith("vpc"):
        appname = "{0}-{1}".format(hostnames[0], hostnames[1])
    elif len(hostnames) > 5:
        appname = "{0}-{1}-{2}".format(hostnames[0], hostnames[1], hostnames[2])
    elif len(hostnames) > 4:
        appname = "{0}-{1}".format(hostnames[0], hostnames[1])
    else:
        logging.error("getAppname error")
        exit(1)
    return appname

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Log Archive Script")
    parser.add_argument("-t", "--rever_day", nargs='?', help="All the logs from a few days ago were archived", default=0)
    parser.add_argument("-d", "--ddurl", nargs='?', help="DingDing Group chat robot", default="https://oapi.dingtalk.com/robot/send?access_token=xxx")
    parser.add_argument("-s", "--source", nargs='?', help="exec origin", default="cron")
    args = parser.parse_args()
    rever_day = args.rever_day
    ddurl = args.ddurl
    exec_source = args.source

    logfile = {
        "app-web01": {"type": "del", "dir": ["/data0/log-data/web01/"], "rule": [r"\b\d{4}-\d{2}-\d{2}\b"]},

        "app-web02": {"type": "empty","dir": ["/data0/log-data/"], "rule": [r"\bsports\d{1}\b", r"\btech\d{1}\b"]},

        "app-web03": {"type": "tar", "dir": ["/data0/log-data/"], "rule": [r"\b\d{4}-\d{2}-\d{2}\b"], "day": 1}
    }

    appname = getAppname()
    log_appname = logfile.get(appname)

    rules = log_appname.get("rule")
    if log_appname.get("day"):
        rever_day = log_appname.get("day")
    Log=logHandle(rules, rever_day)

    value, ok = Log.runCmd("df -h |head -n 2 |tail -n 1 |awk '{print $5}' |awk -F'%' '{print $1}'")
    if operator.lt(int(value), 80):
        if log_appname.get("type") != "tar":
            value, ok = Log.runCmd("df -h |grep data0 |head -n 2 |tail -n 1 |awk '{print $5}' |awk -F'%' '{print $1}'")
            if value:
                if operator.lt(int(value), 80):
                    exit(0)
            else:
                exit(0)

    if not log_appname:
        mes = u"找不到应用清理计划"
    else:
        if str(exec_source) != "cron" and log_appname.get("type") == "tar":
            exit(0)
        for Logdir in log_appname.get("dir"):
            Files = Log.file_list(Logdir)
            if not Files:
                break
            elif log_appname.get("type") == "del":
                _date_list = Log.keyword_list(Files)
                _rever_date_list = Log.rever_date_list(_date_list)
                Log.del_log(Logdir, Files, _rever_date_list)
            elif log_appname.get("type") == "empty":
                keywords = Log.keyword_list(Files)
                Log.empty_log(Logdir, Files, keywords)
            elif log_appname.get("type") == "tar":
                # 过滤需要压缩的日期列表
                _date_list = Log.keyword_list(Files)
                _rever_date_list = Log.rever_date_list(_date_list)
                for _date in _rever_date_list:
                    _dir = None
                    if _date_list:
                        # 过滤.log日志文件
                        filter_files = Log.filter_list(Files, _date)
                        if filter_files:
                            # 归档日志到目录
                            _dir = Log.file_dir(Logdir, filter_files, _date)
                    if os.path.exists(_dir):
                        # 归档目录进行压缩
                        Log.dir_tar(_dir)
                Log.del_tar(7, Logdir)
            else:
                logging.error("{0} type error!".format(log_appname.get("type")))
                exit(1)
        else:
            mes = u"执行应用清理计划"
    # 通用日志清除
    value, ok = Log.runCmd("df -h |head -n 2 |tail -n 1 |awk '{print $5}' |awk -F'%' '{print $1}'")
    if operator.ge(int(value), 80):
        log_list = [
            '/data0/log-data/msv-access.log-{0}'.format(time.strftime("%Y%m%d", time.localtime())),
            '/data0/log-data/tomcat/catalina.out-{0}'.format(time.strftime("%Y%m%d", time.localtime())),
            '/data0/log-data/tomcat/catalina.out',
        ]
        for f in log_list:
            if os.path.exists(f):
                fsize = os.path.getsize(f)/1024/1024
                if operator.ge(fsize,2048):
                    with open(f, 'r+') as f:
                        f.truncate()
            time.sleep(0.1)

    value, ok = Log.runCmd("df -h |head -n 2 |tail -n 1 |awk '{print $5}' |awk -F'%' '{print $1}'")
    if operator.ge(int(value), 88):
        context = u'### 磁盘清理通知： \n\n 应用名: {0} \n\n 描述：{1},清理日志后磁盘使用率为{2}% \n\n'.format(appname, mes, value)
        Log.send_to_rebot(context, ddurl)
