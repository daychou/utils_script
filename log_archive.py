#!/usr/bin/env python

import os
import datetime
import shutil
import tarfile
import re
import argparse


class Log_Archive(object):
    def __init__(self, day=1):
        self.day = day

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
            if date not in _date_list:
                _rever_date_list.append(date)
        return _rever_date_list

    def date_list(self, files):
        '''
        过滤文件的日期字段并写入一个列表
        :param files:文件列表
        :return: 文件列表所在的日期形成一个列表
        '''
        _date_list = []
        for file in files:
            pattern = re.compile(r'\b\d{4}-\d{2}-\d{2}\b')
            log_date = re.findall(pattern, file)
            for _log_date in log_date:
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
                shutil.move('{0}{1}'.format(dir, file), '{0}{1}'.format(_dir, file))
        return _dir

    def dir_tar(self, dir):
        '''
        压缩目录
        :param dir: 目录位置
        :return: 压缩后的文件路径
        '''
        if dir.endswith('/'):
            filename = dir.split('/')[-2]
            dir = os.path.dirname(os.path.dirname(dir))
        else:
            filename = dir.split('/')[-1]
            dir = os.path.dirname(dir)
        tar_filename = dir + '/' + filename + '.tar.gz'
        tar = tarfile.open(tar_filename, "w:gz")
        os.chdir(dir)
        tar.add(filename+'/')
        tar.close()
        if dir and filename:
            shutil.rmtree(dir + '/' + filename)
        return tar_filename

    def del_tar(self, day, Logdir):
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
        for filename in os.listdir(Logdir):
            if filename.endswith('.tar.gz'):
                pattern = re.compile(r'\b\d{4}-\d{2}-\d{2}\b')
                log_date = re.findall(pattern, filename)
                for _log_date in log_date:
                    if _log_date not in time_l:
                        os.remove(Logdir + filename)
        return True

if __name__ == '__main__':
    # 获取日志目录和压缩日志保留天数
    parser = argparse.ArgumentParser(description="Log Archive Script")
    parser.add_argument("-d", "--logdir", nargs='?', help="Log Dir", default='/data0/log-data/debug/')
    parser.add_argument("-t", "--rever_day", nargs='?', help="All the logs from a few days ago were archived", default=1)
    args = parser.parse_args()
    Logdir = args.logdir
    rever_day = args.rever_day
    Log=Log_Archive(rever_day)
    # 文件列表
    Files = Log.file_list(Logdir)
    if Files:
        # 过滤需要压缩的日期列表
        _date_list = Log.date_list(Files)
        _rever_date_list = Log.rever_date_list(_date_list)
        for _date in _rever_date_list:
            _dir = None
            if _date_list:
                # 过滤.log日志文件
                filter_files = Log.filter_list(Files, _date)
                if filter_files:
                    # 归档日志到目录
                    _dir = Log.file_dir(Logdir, filter_files, _date)
            if _dir:
                # 归档目录进行压缩
                Log.dir_tar(_dir)
    Log.del_tar(8, Logdir)