#!/usr/bin/env python
# # -*- coding: UTF-8 -*-
# 
# # This is a _very simple_ example of a web service that recognizes faces in uploaded images.
# Upload an image file and it will check if the image contains a picture of Barack Obama.
# The result is returned as json. For example:
#
# $ curl -XPOST -F "file=@20190321081141.jpg" http://192.168.2.70:5001/face/image/matchN
# curl -XPOST -F "file=@john1.jpg" http://192.168.2.70:5001/face/image/matchN
# curl -H "Accept: application/json" -H "Content-type: application/json"  -d '{"id":100}' -X POST -F "file=@john1.jpg" http://192.168.2.70:5001/face/image/matchN
#
# Returns:
#
# {
#  "face_found_in_image": true,
#  "is_picture_of_obama": true
# }
#
# This example is based on the Flask file upload example: http://flask.pocoo.org/docs/0.12/patterns/fileuploads/

# NOTE: This example requires flask to be installed! You can install it with pip:
# $ pip3 install flask

import face_recognition
from flask import Flask, jsonify, request, redirect, abort, make_response, current_app

from datetime import timedelta
from functools import update_wrapper

try:    
    from flask_cors import CORS, cross_origin  # The typical way to import flask-cors
except ImportError:
    # Path hack allows examples to be run without installation.
    import os
    parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.sys.path.insert(0, parentdir)

    from flask_cors import CORS, cross_origin

import base64
import os
import time
import datetime
import logging

from enum import Enum, unique

import pickle
import numpy as np

logging.getLogger('flask_cors').level = logging.DEBUG

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@unique
class Mode(Enum):
    m1_1 = 0 # 1:1
    m1_N = 1 # 1:N


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

console_out('logging.log')



# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# https://stackoverflow.com/questions/46586345/how-to-run-function-before-flask-routing-is-starting
# app = Flask(__name__)

tolerance = 0.4

known_faces = [
    ]

known_faces_name = [
    ]

all_face_encodings = {}

known_faces_path = './pics'
unknown_faces_path = './pics/tmp/'
new_faces_path = './pics/new/'



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


###############################################################################
# Load the jpg files into arrays
###############################################################################
def initFacesFromDatafile():
   
    global known_faces
    global known_faces_name
    global all_face_encodings

    if( len(known_faces) != 0):
        return

    logging.debug("--------------- Loading known faces from data file ---------")    

    start_time = time.time()  

    # Load face encodings
    with open('dataset_faces.dat', 'rb') as f:
	    all_face_encodings = pickle.load(f)

    # Grab the list of names and the list of encodings
    known_faces_name = list(all_face_encodings.keys())
    # known_faces = np.array(list(all_face_encodings.values()))
    known_faces = (list(all_face_encodings.values()))

    logging.debug("=============== load {} faces use {} seconds ===============" 
        .format( len(known_faces_name), round((time.time() - start_time), 2)) )

###############################################################################


def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
    return response


def create_app():
    print "Testing Cors ..."

    # initFaces()
    initFacesFromDatafile()    
    app = Flask(__name__)
    app.after_request(after_request)
    CORS(app)


    # 

    # app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
    # app.config['CORS_HEADERS'] = 'Content-Type'

    # cors = CORS(app, resources={r"/face/image/match": {"origins": "http://192.168.2.76:5001"}})

    return app

app = create_app()

# CORS(app, resources=r'/face/*')

###############################################################################
# Load the jpg files into arrays
###############################################################################
def initFaces():
    global known_faces
    global known_faces_name

    if( len(known_faces) != 0):
        return

    logging.debug("---------------------------------------- Loading known faces ----------------------------------------")    

    start_time = time.time()  
    for filename in os.listdir(known_faces_path):
        if filename.endswith(".png") or filename.endswith(".jpg"): 
            logging.debug(os.path.join(known_faces_path, filename ))
            
            username = os.path.splitext(filename)[0]

            load_image = face_recognition.load_image_file( os.path.join(known_faces_path, filename) )
            # logging.debug("load_image_file use %s seconds" % round((time.time() - start_time), 2))

            # start_time = time.time()  
            load_image_encoding = face_recognition.face_encodings(load_image)[0]
            # logging.debug(load_image_encoding)
            # logging.debug("face_encodings use %s seconds" % round((time.time() - start_time), 2))
            all_face_encodings[ username ] = load_image_encoding

            # start_time = time.time()  
            known_faces_name.append( username )
            known_faces.append( load_image_encoding )
            # logging.debug("append use %s seconds" % round((time.time() - start_time), 2))

            continue
        else:
            continue

    logging.debug("======================================== use %s seconds ========================================" % round((time.time() - start_time), 2))

    with open('dataset_faces.dat', 'wb') as f:
        pickle.dump(all_face_encodings, f)
    
    logging.debug("======================================== use %s seconds ========================================" % round((time.time() - start_time), 2))
  
###############################################################################

















@app.route('/face/feature/add', methods=['POST'])
def featureAdd():

    global known_faces
    global known_faces_name
    global all_face_encodings

    if not request.json or not 'username' in request.json:
        abort(400)

    if not request.json or not 'template' in request.json:
        abort(400)

    # For data is Base64
    username = request.json['username']
    imgdata = base64.b64decode( request.json['template'] )
    
    file_stream = new_faces_path + username + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.jpg'  # I assume you have a way of picking unique filenames
    # logging.debug("save data stream to file: " + file_stream) 
    # logging.debug filename
    with open(file_stream, 'wb') as f:
        f.write(imgdata)

    load_image = face_recognition.load_image_file( file_stream )
    load_image_encoding = face_recognition.face_encodings(load_image)[0]
    all_face_encodings[ username ] = load_image_encoding

    known_faces_name.append( username )
    known_faces.append( load_image_encoding )

    with open('dataset_faces.dat', 'wb') as f:
        pickle.dump(all_face_encodings, f)

    result = {
            "username": username,
            "info": "success",       
        }

    return jsonify(result)


@app.route('/face/image/matchN', methods=['POST'])
def matchN():

    ######################################## check ######################################## 
    if not request.json or not 'format' in request.json:
        format = "png"
    
    if not request.json or not 'groupid' in request.json:
        groupid = "yunnanca:tech"

    if not request.json or not 'top' in request.json:
        top = 1

    if not request.json or not 'username' in request.json:
        logging.debug("1:N mode") 
        username = "user"
    else:
        username = request.json['username']
    ###############################################################################    


    # $ curl -XPOST -F "file=@obama2.jpg" http://192.168.10.10:5001/face/image/matchN
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' in request.files:     
            logging.debug("Get Http Post file") 

            file_stream = request.files['file']

            if file_stream.filename == '':
                return redirect(request.url)

            if file_stream and allowed_file(file_stream.filename):
              
                logging.debug("call compare_faces_with_image") 
                # The image file seems valid! Detect faces and return the result.
                return compare_faces_with_image(file_stream, file_stream.filename)
        else:
            logging.debug("Try to check Http Post Body") 


    if not request.json or not 'data' in request.json:
        abort(400)   

    # For data is Base64
    imgdata = base64.b64decode( request.json['data'] )
    

    file_stream = unknown_faces_path + username + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.jpg'  # I assume you have a way of picking unique filenames
    logging.debug("save data stream to file: " + file_stream) 
    # logging.debug filename
    with open(file_stream, 'wb') as f:
        f.write(imgdata)

    logging.debug("call compare_faces_with_image") 
    return compare_faces_with_image(file_stream, username, Mode.m1_N)




@app.route('/face/image/match', methods=['POST',  'OPTIONS'])
@crossdomain(origin='*')
def match():

    ######################################## check ######################################## 
    if not request.json or not 'format' in request.json:
        format = "png"
    
    if not request.json or not 'groupid' in request.json:
        groupid = "yunnanca:tech"

    if not request.json or not 'top' in request.json:
        top = 1

    if not request.json or not 'username' in request.json:
        logging.debug("1:N mode") 
        username = "user"
    else:
        username = request.json['username']
    ###############################################################################    


    # $ curl -XPOST -F "file=@obama2.jpg" http://192.168.10.10:5001/face/image/matchN
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' in request.files:     
            logging.debug("Get Http Post file") 

            file_stream = request.files['file']

            if file_stream.filename == '':
                return redirect(request.url)

            if file_stream and allowed_file(file_stream.filename):
              
                logging.debug("call compare_faces_with_image") 
                # The image file seems valid! Detect faces and return the result.
                return compare_faces_with_image(file_stream, file_stream.filename)
        else:
            logging.debug("Try to check Http Post Body") 


    if not request.json or not 'data' in request.json:
        abort(400)
    task = {
        'data': request.json['data'],        
    }
    # logging.debug request.json['data']

    # For data is Base64
    imgdata = base64.b64decode( request.json['data'] )
    

    file_stream = unknown_faces_path + username + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.jpg'  # I assume you have a way of picking unique filenames
    logging.debug("save data stream to file: " + file_stream) 
    # logging.debug filename
    with open(file_stream, 'wb') as f:
        f.write(imgdata)

    logging.debug("call compare_faces_with_image") 
    return compare_faces_with_image(file_stream, username)





def compare_faces_with_image(file_stream, username, mode = Mode.m1_1):  

    global known_faces
    global known_faces_name

    try:

        process_username = os.path.splitext(username)[0]

        unknown_face_encoding = ""

        # logging.debug('file_stream')
        # logging.debug file_stream
        # logging.debug('username='+username)

        begin_time = time.time()

        # Load the uploaded image file
        img = face_recognition.load_image_file(file_stream)
        logging.debug("## Load the uploaded image file         in %s seconds ##" % round((time.time() - begin_time), 2) )

        start_time = time.time()
        # Get face encodings for any faces in the uploaded image
        
        unknown_face_encodings = face_recognition.face_encodings(img)
        unknown_face_encoding = unknown_face_encodings[0]
        logging.debug("## face_encodings                       in %s seconds ##" %  round((time.time() - start_time), 2)      )

        if(mode.value == 0):
            # str(mode.value)
            logging.debug("##################### 1:1 Mode ###########################")                        

            start_time = time.time()
            # Load the jpg files into numpy arrays
            file_path = os.path.join(known_faces_path, process_username + ".jpg")

            username_image = face_recognition.load_image_file( file_path )
            logging.debug("## load_image_file " + file_path + " in %s seconds ##" % round((time.time() - start_time), 2))

            start_time = time.time()
            username_face_encoding = face_recognition.face_encodings(username_image)[0]
            logging.debug("## face_encodings                       in %s seconds ##" % round((time.time() - start_time), 2))
            
            local_known_faces = [
                username_face_encoding,
            ]

            start_time = time.time()
            results = face_recognition.compare_faces(local_known_faces, unknown_face_encoding, tolerance)
            logging.debug("## compare_faces                        in %s seconds ##" % round((time.time() - start_time), 2))       

            if ( results[0] ):            
                face_found = True
            else:
                face_found = False
        else:
            logging.debug("##################### 1:N Mode ###########################")

            results = face_recognition.compare_faces(known_faces, unknown_face_encoding, tolerance)
            logging.debug("## compare_faces                        in %s seconds ##" % round((time.time() - start_time), 2))  

            logging.debug(known_faces_name)
            logging.debug(results)

            face_found = False
            for index in range(len(results)):
                if results[index] == True:
                    face_found = True
                    process_username = known_faces_name[index]
                    break
     
    except IndexError:
        face_found = False   
    except IOError:
        if unknown_face_encoding == "":
            result = {
                "info": "failed",       
            }
            logging.debug(result)
            return jsonify(result)
        else:    
            logging.debug("##################### 1:N Mode ###########################")
                    
            results = face_recognition.compare_faces(known_faces, unknown_face_encoding, tolerance)
            logging.debug("## compare_faces                        in %s seconds ##" % round((time.time() - start_time), 2))  

            logging.debug(known_faces_name)
            logging.debug(results)

            face_found = False
            for index in range(len(results)):
                if results[index] == True:
                    face_found = True
                    process_username = known_faces_name[index]
                    break

    logging.debug("## compare_faces_with_image used in total  %s seconds ##" % round((time.time() - begin_time), 2))
    logging.debug("##########################################################")  

    # Return the result as json
    if ( face_found ):
        result = {
            "username": process_username,
            "info": "success",       
        }
    else:
        result = {
            "info": "user " + process_username +" not found"
        }

    logging.debug(result)
    return jsonify(result)
    
    
    







if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)


