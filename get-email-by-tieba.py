#! /usr/bin/env python
# -*- coding: utf-8 -*-
#@author 昌维 [867597730@qq.com]
#@version 2016-07-28 21:05:47

import urllib2
import urllib
import hashlib
import json
import re
import sys
import getopt
import time

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

def main():
	print """
*****************************************
*      Get Tieba's Email&Telephone      *
*           Code By changwei            *
*****************************************
author  : changwei
date    : 2016-07-28 21:05:47
email   : 867597730@qq.com
website : www.changwei.me
-----------------------------------------
usage        : <-t thread_id | -f forum_name -s start_page -e end_page> <-o out_file_path> [-i split_str]
example1     : -t 2314539885 -o C:\info.txt
example2     : -f bug -o C:\info.txt
example3     : -f bug -o C:\info.txt -i ------
output_file3 : robin------robin@baidu.com
-----------------------------------------
	"""
	# print sys.argv
	opts, args    = getopt.getopt(sys.argv[1:], "t:f:s:e:o:i:")
	thread_id           = ''
	forum_name    = ''
	start_page    = ''
	end_page      = ''
	out_file_path = ''
	split_str     = ''
	for op, value in opts:
		if op == "-t":
			thread_id = value
		elif op == "-f":
			forum_name = value
		elif op == "-s":
			start_page = int(value)
		elif op == "-e":
			end_page = int(value)
		elif op == "-o":
			out_file_path = value
		elif op == "-i":
			split_str = value

	info = [] # 用于存储fetch结果

	if thread_id == '' and forum_name == '':
		print '1.fetch by forum_name\n2.fetch by thread_id'
		fetch_type = raw_input("please press the fetch type:")
		# print '-----------------------------------------\nplease input the parameter'
		if fetch_type=='1': # fetch by forum_name
			forum_name = raw_input("please input the forum_name:")
			start_page = raw_input("please input the start_page:")
			end_page = raw_input("please input the end_page:")
			out_file_path = raw_input("please input the out_file_path:")
			info = info + fetchByForumName(forum_name,start_page,end_page,split_str)
		elif fetch_type=='2': # fetch by thread_id
			thread_id = raw_input("please input the thread_id:")
			out_file_path = raw_input("please input the out_file_path:")
			info = info + fetchByThreadId(thread_id,split_str)
		else:
			print 'error input!!!'
	elif thread_id != '' and out_file_path != '':
		info = info + fetchByThreadId(thread_id,split_str)
	elif forum_name != '' and start_page != '' and end_page != '' and out_file_path != '':
		info = info + fetchByForumName(forum_name,start_page,end_page,split_str)
	else:
		print 'error input!!!'
		return

	write_to_file(out_file_path,info)
	print 'Please open the file. Path:[' + out_file_path + ']'
	# print thread
	# thread['post_list']['0']['content']['0']['text'] content同级[author][name]为id
	# thread['thread']['valid_post_num']
	# print getInfoByInput('867597730@qq.com,635491570@qq.com,lol@changwei.me,18970459733,12345678901')
	#
def initInfo():
	ISOTIMEFORMAT='%Y-%m-%d %X'
	print '' + time.strftime( ISOTIMEFORMAT, time.localtime() ) + '   start!!!\n'

def write_to_file(out_file_path,content):
	'写入content集合到out_file_path里面，此处content为抓取得到的数据，数据类型为list，用户可以手动修改保存方式，比如说保存在数据库或者json里面等等'
	file = open(out_file_path,'a')
	file.writelines(content)
	print content

def fetchByForumName(forum_name,start_page,end_page,split_str=''):
	'从指定贴吧中抓取邮箱和手机号数据'
	initInfo()
	info = []
	tids = getTidsByKw(forum_name,start_page,end_page)
	for tid in tids:
		if tid == '':continue
		thread_json = getThreadByTid(tid=tid,pn='0')
		thread = json.loads(thread_json)
		pn_total = int(thread['thread']['valid_post_num']) / 30 + 1
		for x in xrange(0,pn_total):
			thread_json = getThreadByTid(tid=tid,pn=str(x))
			thread = json.loads(thread_json)
			for thread_text in thread['post_list']:
				# print thread_text['content']
				if len(thread_text['content'])>0:
					if thread_text['content'][0].has_key('text'):
						if len(getInfoByInput(thread_text['content'][0]['text'].encode('utf8')))!=0:
							if split_str == '':
								info.append(getInfoByInput(thread_text['content'][0]['text'].encode('utf8')) + '\n')
							else:
								info.append(getInfoByInput(thread_text['content'][0]['text'].encode('utf8')) + split_str + thread_text['author']['name'].encode('utf8') + '\n')
	return info

def fetchByThreadId(tid,split_str=''):
	'从指定帖子中抓取邮箱和手机号数据'
	initInfo()
	info = []
	thread_json = getThreadByTid(tid=tid,pn='0')
	thread = json.loads(thread_json)
	pn_total = int(thread['thread']['valid_post_num']) / 30 + 1
	for x in xrange(0,pn_total):
		thread_json = getThreadByTid(tid=tid,pn=str(x))
		thread = json.loads(thread_json)
		for thread_text in thread['post_list']:
			# print thread_text['content'][0]['text'].encode('utf8')
			if len(thread_text['content'])>0:
				if thread_text['content'][0].has_key('text'):
					if len(getInfoByInput(thread_text['content'][0]['text'].encode('utf8')))!=0:
						if split_str == '':
							info.append(getInfoByInput(thread_text['content'][0]['text'].encode('utf8')) + '\n')
						else:
							info.append(getInfoByInput(thread_text['content'][0]['text'].encode('utf8')) + split_str + thread_text['author']['name'].encode('utf8') + '\n')
	return info

def getThreadByTid(tid,pn='0'):
	'通过tid获取帖子内容'
	data =  ['_client_id=wappc_1396611108603_817',
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
	data.append("sign="+getSignByPostData(data))
	#定义post的地址
	url = 'http://c.tieba.baidu.com/c/f/pb/page'
	# post_data = urllib.urlencode(data)
	post_data = "&".join(data)
	# 设置头部
	headers = { 'Content-Type':'application/x-www-form-urlencoded',
	'Referer':'http://tieba.baidu.com/',
	'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0',
	'Connection':'keep-alive' }
	# req.add_header('Content-Type','application/x-www-form-urlencoded');
	# req.add_header('Referer','http://tieba.baidu.com/');
	# req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0');
	# req.add_header('Connection','keep-alive');
	# print post_data
	#提交，发送数据
	req = urllib2.Request(url, post_data, headers)
	response = urllib2.urlopen(req)
	#获取提交后返回的信息
	content = response.read()
	return content

def getTidsByKw(kw='',start_page='0',end_page=''):
	'通过贴吧名获取帖子号列表'
	tids = []
	for pn in xrange(int(start_page),int(end_page)):
		data =  [
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
		data.append("sign="+getSignByPostData(data))
		#定义post的地址
		url = 'http://c.tieba.baidu.com/c/f/frs/page'
		# post_data = urllib.urlencode(data)
		post_data = "&".join(data)
		# 设置头部
		headers = { 'Content-Type':'application/x-www-form-urlencoded',
		'Referer':'http://tieba.baidu.com/',
		'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0',
		'Connection':'keep-alive' }
		# req.add_header('Content-Type','application/x-www-form-urlencoded');
		# req.add_header('Referer','http://tieba.baidu.com/');
		# req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0');
		# req.add_header('Connection','keep-alive');
		# print post_data
		#提交，发送数据
		req = urllib2.Request(url, post_data, headers)
		response = urllib2.urlopen(req)
		#获取提交后返回的信息
		content = response.read()
		forum_json = json.loads(content)
		tids = tids + forum_json['forum']['tids'].split(',')
	return tids

def getSignByPostData(post_data):
	'通过post数据获得sign校验码'
	sign = hashlib.md5()
	# print "".join(post_data)
	sign.update("".join(post_data)+"tiebaclient!!!")
	return sign.hexdigest()

def getInfoByInput(inputmail):
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
	regex = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}|1[3|4|5|7|8]\d{9}\b", re.IGNORECASE)
	result = str(re.findall(regex, inputmail)).replace("']",'').replace("['",'').replace("[]",'').replace("', '",'')
	return result

if __name__ == '__main__':
	start_time = time.time()
	main()
	end_time = time.time()
	print '\nFinished in ' + str(end_time - start_time) + 's'
	print "Get Tieba's Email&Telephone. Code By changwei[867597730@qq.com]"