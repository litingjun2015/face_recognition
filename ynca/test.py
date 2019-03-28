#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import requests
import base64
import json

print "it's testing ..."



# print encoded_string



headers = \
    {
        "X-Member-Id": "23832170000",
        "X-Region": "1100000",
        "X-Channel": "01",
        "Content-Type": "application/json;charset=UTF-8"
    }

import os
import logging

test_faces_path = "./pics/test2/"

def console_out(logFilename):
    ''' Output log to file and console '''
    # Define a Handler and set a format which output to file
    logging.basicConfig(
                    level    = logging.DEBUG,              # 定义输出到文件的log级别，                                                            
                    format   = '%(asctime)s  %(filename)s : %(levelname)s  %(message)s',    # 定义输出log的格式
                    datefmt  = '%Y-%m-%d %A %H:%M:%S',                                     # 时间
                    filename = logFilename,                # log文件名
                    filemode = 'w')                        # 写入模式“w”或“a”
    # Define a Handler and set a format which output to console
    console = logging.StreamHandler()                  # 定义console handler
    console.setLevel(logging.INFO)                     # 定义该handler级别
    formatter = logging.Formatter('%(asctime)s  %(filename)s : %(levelname)s  %(message)s')  #定义该handler格式
    console.setFormatter(formatter)
    # Create an instance
    logging.getLogger().addHandler(console)           # 实例化添加handler
 
    # Print information              # 输出日志级别
    # logging.debug('logger debug message')     
    # logging.info('logger info message')
    # logging.warning('logger warning message')
    # logging.error('logger error message')
    # logging.critical('logger critical message')



# # create logger
# logger = logging.getLogger("logging_tryout2")
# logger = logging.basicConfig(filename='run.log',level=logging.DEBUG)

console_out('run.log')

for filename in os.listdir(test_faces_path):
        if filename.endswith(".png") or filename.endswith(".jpg"): 
            logging.debug( os.path.join(test_faces_path, filename ))
            
            username = os.path.splitext(filename)[0]

            with open(os.path.join(test_faces_path, filename ), "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                body = \
                {
                    "data": encoded_string
                }
                r = requests.post('http://192.168.2.70:5001/face/image/matchN', headers=headers, data=json.dumps (body) )
                logging.debug(r.text)            
            continue
        else:
            continue




