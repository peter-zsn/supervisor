#coding=utf-8

"""
@varsion: ??
@author: 张帅男
@file: test.py
@time: 2018/1/8 11:02
"""
import time
import sys
import logging
from db_config import get_db
from twisted.internet import reactor
from twisted.application import service

db = get_db(250)

list_tmp = [1, 2, 3, 4, 5, 6, 7]


logging.basicConfig(level=logging.INFO,
                    stream=sys.stdout,
                    format='SCRIPT: %(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='w')

class Worker:
    def handle(self):
        for i in list_tmp:
            result = db.tbkt_yingyu.test.get(id=i)
            logging.info(result.id)
            time.sleep(4)

    def start(self):
        while 1:
            try:
                self.handle()
                logging.info('good exist')
            except Exception, e:
                logging.error(e)

if __name__ == '__main__':
    worker = Worker()
    worker.start()

elif __name__ == '__builtin__':
    print '__builtin__'
    worker = Worker()
    reactor.callInThread(worker.start)
    application = service.Application('task_census_service')
