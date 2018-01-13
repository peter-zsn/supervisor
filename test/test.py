#coding=utf-8

"""
@varsion: ??
@author: 张帅男
@file: test.py
@time: 2018/1/8 11:02
"""
import time
import logging
import sys
from db_config import get_db
from twisted.internet import reactor
from twisted.application import service

db = get_db(250)

list_tmp = [1, 2, 3, 4, 5, 6, 7]

logging.basicConfig(level=logging.INFO,
                    stream=sys.stdout,
                    format='SCRIPT: %(filename)s: %(asctime)s %(name)s %(levelname)s  %(filename)s[line:%(lineno)d func:%(funcName)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='w')

class Worker:
    def handle(self):
        try:
            for i in list_tmp:
                result = db.tbkt_yingyu.test.get(id=i)
                logging.info(result.id)
        except Exception as e:
            logging.error(e)


    def start(self):
        while 1:
            try:
                self.handle()
                logging.info('test good exist')
                time.sleep(4)  # 处理完了 睡4s
            except Exception, e:
                logging.error(e)
                time.sleep(1)  # 报错睡1秒， 继续进行

if __name__ == '__main__':
    worker = Worker()
    worker.start()

elif __name__ == '__builtin__':
    print '__builtin__'
    worker = Worker()
    reactor.callInThread(worker.start)
    application = service.Application('task_census_service')
