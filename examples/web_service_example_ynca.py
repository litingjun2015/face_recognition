# -*- coding: UTF-8 -*-
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
from flask import Flask, jsonify, request, redirect, abort

import base64
import os
import time
import datetime
import logging

from enum import Enum, unique

import pickle
import numpy as np


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

#########################################################################################
# Load the jpg files into arrays
#########################################################################################
def initFacesFromDatafile():
   
    global known_faces
    global known_faces_name

    # TODO
    if( len(known_faces) != 0):
        return

    logging.debug("---------------------------------------- Loading known faces from data file ----------------------------------------")    

    start_time = time.time()  

    # Load face encodings
    with open('dataset_faces.dat', 'rb') as f:
	    all_face_encodings = pickle.load(f)

    # Grab the list of names and the list of encodings
    known_faces_name = list(all_face_encodings.keys())
    known_faces = np.array(list(all_face_encodings.values()))

  
    logging.debug("======================================== use %s seconds ========================================" % round((time.time() - start_time), 2))

    with open('dataset_faces.dat', 'wb') as f:
        pickle.dump(all_face_encodings, f)
    
    logging.debug("======================================== use %s seconds ========================================" % round((time.time() - start_time), 2))
#########################################################################################


#########################################################################################
# Load the jpg files into arrays
#########################################################################################
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

    # biden_image = face_recognition.load_image_file("biden.jpg")
    # obama_image = face_recognition.load_image_file("obama.jpg")
    # litingjun_image = face_recognition.load_image_file("litingjun.jpg")

    # biden_face_encoding = face_recognition.face_encodings(biden_image)[0]
    # obama_face_encoding = face_recognition.face_encodings(obama_image)[0]
    # litingjun_face_encoding = face_recognition.face_encodings(litingjun_image)[0]    

    # known_faces_name.append("biden")
    # known_faces_name.append("obama")
    # known_faces_name.append("litingjun")

    # known_faces.append(biden_face_encoding)
    # known_faces.append(obama_face_encoding)
    # known_faces.append(litingjun_face_encoding)
#########################################################################################

def create_app():
    # initFaces()
    initFacesFromDatafile()
    return Flask(__name__)






app = create_app()


def detect_faces_in_image(file_stream):

    face_found = False
    start_time = time.time()

    # Load the uploaded image file
    unknown_image = face_recognition.load_image_file(file_stream)
    # logging.debug(unknown_image)
    try:
        # Get face encodings for any faces in the uploaded image
        unknown_face_encodings = face_recognition.face_encodings(unknown_image)
        # logging.debug(unknown_face_encodings)
        unknown_face_encoding = unknown_face_encodings[0]
        # logging.debug(unknown_face_encoding)
        results = face_recognition.compare_faces(known_faces, unknown_face_encoding)
        logging.debug(results) 
        
        if (not True in results):
            logging.debug("该图片没有在我们的人脸库中")

        i = 0
        for result in results:
            
            if result and known_faces_name[i] != "tmp": 
                face_found = True
                username = known_faces_name[i]           

            i = i+1

        logging.debug("--- detect_faces_in_image used %s seconds ---" % round((time.time() - start_time), 2))

    except IndexError:
        logging.debug("该图片没有在我们的人脸库中，请重新拍摄")
    

    # Return the result as json
    if ( face_found ):
        result = {
            "username": username,
            "info": "success",       
        }
    else:
        result = {
            "info": "failed"
        }
    
    
    return jsonify(result)




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




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
    #########################################################################################    


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
    return compare_faces_with_image(file_stream, username, Mode.m1_N)




@app.route('/face/image/match', methods=['POST'])
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
    #########################################################################################    


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






@app.route('/', methods=['GET', 'POST'])
def upload_image():
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # The image file seems valid! Detect faces and return the result.
            return detect_faces_in_image(file)

    # If no valid image file was uploaded, show the file upload form:
    return '''
    <!doctype html>
    <title>Is this a picture of Obama?</title>
    <h1>Upload a picture and see if it's a picture of Obama!</h1>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''




def compare_faces_with_image(file_stream, username, mode = Mode.m1_1):  

    global known_faces
    global known_faces_name

    try:

        process_username = os.path.splitext(username)[0]

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
