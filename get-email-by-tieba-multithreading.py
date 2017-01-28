#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @author 昌维 [867597730@qq.com]
# @version 2016-07-28 21:05:47

import Queue
import getopt
import hashlib
import json
import re
import sys
import threading
import time
import urllib
import urllib2

import MySQLdb
import cmd_color_printers

reload(sys)
sys.setdefaultencoding('utf-8')

# class UnicodeStreamFilter:
# 	def __init__(self, target):
# 		self.target = target
# 		self.encoding = 'utf-8'
# 		self.errors = 'replace'
# 		self.encode_to = self.target.encoding
# 	def write(self, s):
# 		if type(s) == str:
# 			s = s.decode("utf-8")
# 		s = s.encode(self.encode_to, self.errors).decode(self.encode_to)
# 		self.target.write(s)

# if sys.stdout.encoding == 'cp936':
# 	sys.stdout = UnicodeStreamFilter(sys.stdout)

def data_processing(content):
    '写入content集合到out_file_path里面，此处content为抓取得到的数据，数据类型为list，用户可以手动修改保存方式，比如说保存在数据库或者json里面等等'
    file = open(out_file_path, 'a')
    file.writelines(content)
    print content
    print 'Please open the file. Path:[' + out_file_path + ']'


def fetchByForumName(forum_name, start_page, end_page, split_str=''):
    '从指定贴吧中抓取邮箱和手机号数据'
    initInfo()
    info = []
    tids = getTidsByKw(forum_name, start_page, end_page)
    for tid in tids:
        if tid == '': continue
        thread_json = getThreadByTid(tid=tid, pn='0')
        thread = json.loads(thread_json)
        pn_total = int(thread['thread']['valid_post_num']) / 30 + 1
        for x in xrange(0, pn_total):
            thread_json = getThreadByTid(tid=tid, pn=str(x))
            thread = json.loads(thread_json)
            for thread_text in thread['post_list']:
                # print thread_text['content']
                if len(thread_text['content']) > 0:
                    if thread_text['content'][0].has_key('text'):
                        if len(getInfoByInput(thread_text['content'][0]['text'].encode('utf8'))) != 0:
                            if split_str == '':
                                info.append(getInfoByInput(thread_text['content'][0]['text'].encode('utf8')) + '\n')
                            else:
                                info.append(
                                    getInfoByInput(thread_text['content'][0]['text'].encode('utf8')) + split_str +
                                    thread_text['author']['name'].encode('utf8') + '\n')
    return info


def fetchByThreadId(tid):
    '从指定帖子中抓取邮箱和手机号数据'
    # global tieba
    info_list = []
    thread_json = getThreadByTid(tid=tid, pn='0')
    thread = json.loads(thread_json)
    if thread is None or 'thread' not in thread:
        return []
    pn_total = int(thread['thread']['valid_post_num']) / 30 + 1
    for x in xrange(0, pn_total):
        thread_json = getThreadByTid(tid=tid, pn=str(x))
        thread = json.loads(thread_json)
        for thread_text in thread['post_list']:
            # print thread_text['content'][0]['text'].encode('utf8')
            if len(thread_text['content']) > 0:
                if thread_text['content'][0].has_key('text'):
                    info = getInfoByInput(thread_text['content'][0]['text'].encode('utf8'))
                    if len(info) != 0:
                        info_dict = {}
                        info_dict['tieba'] = thread['forum']['name']
                        info_dict['name'] = thread_text['author']['name']
                        info_dict['email'] = info['email']
                        info_dict['telephone'] = info['phone']
                        info_dict['thread'] = thread_text['content'][0]['text'].encode('utf8')
                        info_dict['tid'] = tid
                        info_dict['cid'] = thread_text['id']
                        info_list.append(info_dict)
    return info_list


def getThreadByTid(tid, pn='0'):
    '通过tid获取帖子内容'
    data = ['_client_id=wappc_1396611108603_817',
            '_client_type=2',
            '_client_version=5.7.0',
            '_phone_imei=642b43b58d21b7a5814e1fd41b08e2a6',
            'from=tieba',
            'kz=' + tid,
            'pn=' + pn,
            'q_type=2',
            'rn=30',
            'with_floor=1']
    # print getSignByPostData(data)
    # print data
    data.append("sign=" + getSignByPostData(data))
    # 定义post的地址
    url = 'http://c.tieba.baidu.com/c/f/pb/page'
    # post_data = urllib.urlencode(data)
    post_data = "&".join(data)
    # 设置头部
    headers = {'Content-Type': 'application/x-www-form-urlencoded',
               'Referer': 'http://tieba.baidu.com/',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0',
               'Connection': 'keep-alive'}
    # req.add_header('Content-Type','application/x-www-form-urlencoded');
    # req.add_header('Referer','http://tieba.baidu.com/');
    # req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0');
    # req.add_header('Connection','keep-alive');
    # print post_data
    # 提交，发送数据
    req = urllib2.Request(url, post_data, headers)
    response = urllib2.urlopen(req)
    # 获取提交后返回的信息
    content = response.read()
    return content


def getTidsByKw(kw='', start_page=0, end_page=0):
    '通过贴吧名获取帖子号列表'
    tids = []
    for pn in xrange(start_page, end_page):
        data = [
            '_client_id=wappc_1396611108603_817',
            '_client_type=2',
            '_client_version=5.7.0',
            '_phone_imei=642b43b58d21b7a5814e1fd41b08e2a6',
            'from=tieba',
            'kw=' + kw,
            'pn=' + str(pn),
            'q_type=2',
            'rn=30',
            'with_group=1']
        # print getSignByPostData(data)
        # print data
        data.append("sign=" + getSignByPostData(data))
        # 定义post的地址
        url = 'http://c.tieba.baidu.com/c/f/frs/page'
        # post_data = urllib.urlencode(data)
        post_data = "&".join(data)
        # 设置头部
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Referer': 'http://tieba.baidu.com/',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0',
                   'Connection': 'keep-alive'}
        # req.add_header('Content-Type','application/x-www-form-urlencoded');
        # req.add_header('Referer','http://tieba.baidu.com/');
        # req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0');
        # req.add_header('Connection','keep-alive');
        # print post_data
        # 提交，发送数据
        req = urllib2.Request(url, post_data, headers)
        response = urllib2.urlopen(req)
        # 获取提交后返回的信息
        content = response.read()
        forum_json = json.loads(content)
        tids = tids + forum_json['forum']['tids'].split(',')
    return tids


def getSignByPostData(post_data):
    '通过post数据获得sign校验码'
    sign = hashlib.md5()
    # print "".join(post_data)
    sign.update("".join(post_data) + "tiebaclient!!!")
    return sign.hexdigest()


def getInfoByInput(input):
    """
    说明：
    [^\._-][\w\.-]+@(?:[A-Za-z0-9]+\.)+[A-Za-z]+$匹配邮箱。
    综合目前国内常用的邮箱，大概通用的规则包括：
    1、[^\._]，不能以下划线和句点开头。
    2、[\w\.]+，包括字母、数字。而对句点及下划线各提供商有差别，对此有效性不做更严格的判断。
    3、@是必须的。
    4、(?:[A-Za-z0-9]+\.)+[A-Za-z]+$，@后以xxx.xxx结尾，考虑到多级域名，会有这种情况xxx.xxx.xxx如xxx@yahoo.com.cn

    ^0\d{2,3}\d{7,8}$|^1[358]\d{9}$|^147\d{8}$匹配电话号码。
    只考虑国内的情况,大概通用的规则包括：
    1、^0\d{2,3}，固定电话区号3-4位数字，以0开头。
    2、d{7,8}$，固定电话一般7-8位数字。
    3、国内目前的手机号码都是11位数字，三大运营商的号码段基本都在上面列出来了，我们这里除了147的号码的段，其他的都只考虑前两位，
    第三位就不考虑了，否则，工作量也很大。前两位包括13*、15*、18*。
    """
    # p=re.compile('[^\._-][\w\.-]+@(?:[A-Za-z0-9]+\.)+[A-Za-z]+$|^0\d{2,3}\d{7,8}$|^1[358]\d{9}$|^147\d{8}')
    # match = p.match(inputmail)
    # return match.group()
    #
    regex_email = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b", re.IGNORECASE)
    regex_phone = re.compile(r"1[3|4|5|7|8]\d{9}\b", re.IGNORECASE)
    result = {}
    result['email'] = re.findall(regex_email, input)
    result['phone'] = re.findall(regex_phone, input)
    return result


class Worker(threading.Thread):
    """通过tid抓取帖子内容并且匹配出邮箱和手机号"""

    def __init__(self, db):
        threading.Thread.__init__(self)
        self.db = db

    def run(self):
        while True:
            tid = tids_queue.get()
            print('fetch thread by tid : ' + tid)
            info = fetchByThreadId(tid)
            for x in info:
                if len(x['email']) != 0 or len(x['telephone']) != 0:
                    # # 使用cursor()方法获取操作游标
                    self.cursor = self.db.cursor()
                    print x
                    # sql = "INSERT INTO `tieba` (tieba,name,thread,email,telephone,tid,cid) VALUES (%(tieba)s, %(name)s, %(thread)s, %(email)s, %(telephone)s, %(tid)s, %(cid)s)"
                    sql = "INSERT INTO `tieba` (`tieba`,`name`,`thread`,`email`,`telephone`,`tid`,`cid`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (x['tieba'], x['name'], x['thread'], ','.join(x['email']), ','.join(x['telephone']), x['tid'], x['cid'])
                    try:
                        # 执行SQL语句
                        print sql
                        self.cursor.execute(sql)
                        # 向数据库提交
                        self.db.commit()
                    except Exception, e:
                        # 发生错误时回滚
                        # db.rollback()
                        print e.message
            # signals to queue job is done
            tids_queue.task_done()


"""
========================
昌维 2017-01-03 17:33:44
========================
流程：
1.打开数据库连接，创建数据表结构（如果表不存在的情况下）
2.用户填写配置项
3.创建队列以及线程
4.通过输入的贴吧名字向指定的接口获取帖子id列表
5.将获取到的帖子id列表写入队列
6.根据thread_count创建对应数量的线程，并且将mysql连接句柄分发给每个子线程
7.子线程中从队列中消费任务，消费成功则向队列发送“任务完成信号”
8.使用队列的join将主线程阻塞，防止主线程在创建完线程之后立即退出导致数据丢失
9.队列中的任务全部被消费完毕，join则不再阻塞线程，主线程退出，程序运行结束。
"""
# print fetchByThreadId('2314539886')
# exit()

start_time = time.time()
# 配置
tieba = 'php'
start_page = 0
end_page = 100
thread_count = 50

database_host = '127.0.0.1'
database_username = 'root'
database_password = '123456'
database_dbname = 'tieba'
database_charset = 'utf8'

# 准备工作
# 打开数据库连接
db = MySQLdb.connect(database_host, database_username, database_password, database_dbname, charset=database_charset)
# 使用cursor()方法获取操作游标
cursor = db.cursor()
sql = """
CREATE TABLE IF NOT EXISTS `tieba` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `tieba` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `telephone` varchar(255) DEFAULT NULL,
  `thread` varchar(255) DEFAULT NULL,
  `tid` bigint(20) unsigned NOT NULL,
  `cid` bigint(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=COMPACT;
"""
cursor.execute(sql)

tids_queue = Queue.Queue()
tids_list = getTidsByKw(tieba, start_page, end_page)
print len(tids_list)

if len(tids_list) == 0:
    print "无法抓取到tid"
    quit()

for tid in tids_list:
    tids_queue.put(tid)

for x in range(thread_count):
    t = Worker(MySQLdb.connect(database_host, database_username, database_password, database_dbname, charset=database_charset))
    t.setDaemon(True)
    t.start()

tids_queue.join()
end_time = time.time()
print '\nFinished in ' + str(end_time - start_time) + 's'
print "Code By changwei[867597730@qq.com]"
