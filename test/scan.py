#!/usr/bin/env python
# coding=utf-8
import redis
from threading import Thread
import logging
import Queue
import json
import sys
import os
import hashlib

REDIS_HOST = os.getenv('ES_REDIS_HOST', '192.168.7.250')
REDIS_DB_ID = os.getenv('ES_REDIS_DB_ID', '8')
REDIS_PASSWORD = os.getenv('ES_REDIS_PASSWORD', 'jxtbkt2013!')
COLLECT_UWSGI_LOG = os.getenv('COLLECT_UWSGI_LOG', '')

API_TOKEN = os.getenv('__API_TOKEN', '123456')
NUMBER_WORKER_THREADS = 10
MAX_QUEUE_SIZE = 50
q = Queue.Queue(maxsize=MAX_QUEUE_SIZE)

logging.basicConfig(
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    format='%(asctime)s %(levelname)s %(message)s',
    filename='/scan.log'
)


def get_redis_conn():
    return redis.Redis(host=REDIS_HOST, db=REDIS_DB_ID, password=REDIS_PASSWORD, port=6379)
    # return redis.Redis(host=REDIS_HOST, db=REDIS_DB_ID, password=REDIS_PASSWORD)

# 创建redis连接
rconn = None


def worker():
    global rconn
    while True:
        try:
            c_type, content = q.get()
            content = content.rstrip()
            if c_type == 'uwsgi':
                data = {'api_token': API_TOKEN}
                date, time, data['ip'], data['method'], url, data['status'], data['size'], data['wait'], data['agent'] = content.split(' ', 9)[1:]
                data['uri'] = url.split('?', 1)[0]
                data['created'] = date + ' ' + time
                KEY_LIST = "hn_tbkt_uwsgi"
            elif c_type == 'SCRIPT':
                data = {'api_token': API_TOKEN}
                date, time, data['name_kw'], data['level_kw'], message = content.split(' ', 5)[1:]
                data['message_kw'] = message.lstrip()
                m = hashlib.md5()
                m.update(message.lstrip().encode('UTF-8'))
                data['md5_msg'] = m.hexdigest()
                data['created_dt'] = date + ' ' + time
                KEY_LIST = "test_script"
            else:
                data = {'api_token': API_TOKEN}
                date, time, data['name_kw'], data['level_kw'], message = content.split(' ', 5)[1:]
                data['message_kw'] = message.lstrip()
                m = hashlib.md5()
                m.update(message.lstrip().encode('UTF-8'))
                data['md5_msg'] = m.hexdigest()
                data['created_dt'] = date + ' ' + time
                KEY_LIST = "hn_tbkt_app"
            if rconn == None:
                rconn = get_redis_conn()
            if c_type != 'uwsgi':
                rconn.lpush(KEY_LIST, json.dumps(data))
            elif c_type == 'uwsgi' and COLLECT_UWSGI_LOG == 'True':
                rconn.lpush(KEY_LIST, json.dumps(data))
        except BaseException as e:
            logging.error(e)


for i in range(NUMBER_WORKER_THREADS):
    t = Thread(target=worker)
    t.setDaemon(True)
    t.start()

app_content = None
is_app_content = False

while True:
    line = sys.stdin.readline()
    if line.startswith('UWSGI: '):
        if is_app_content:
            q.put(('app', app_content))
            is_app_content = False
        q.put(('uwsgi', line.rstrip('\n')))
    elif line.startswith('APP: ') and ' ERROR ' in line:
        if is_app_content:
            q.put(('app', app_content))
        is_app_content = True
        app_content = line
    elif line.startswith('APP: ') and 'INFO  ' in line:
        if is_app_content:
            q.put(('app', app_content))
        is_app_content = True
        app_content = line
    elif line.startswith('SCRIPT: ') and 'INFO  ' in line:
        if is_app_content:
            q.put(('SCRIPT', app_content))
        print 11111111
        is_app_content = True
        app_content = line
    elif line.startswith('SCRIPT: ') and 'ERROR  ' in line:
        if is_app_content:
            q.put(('SCRIPT', app_content))
        is_app_content = True
        app_content = line
    elif is_app_content and line == '\n':
        q.put(('app', app_content))
        is_app_content = False
    elif is_app_content:
        app_content += line