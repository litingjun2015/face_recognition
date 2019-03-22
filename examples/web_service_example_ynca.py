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
from flask import Flask, jsonify, request, redirect

import base64
import os
import time
import datetime

# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# https://stackoverflow.com/questions/46586345/how-to-run-function-before-flask-routing-is-starting
# app = Flask(__name__)

known_faces = [
    ]

known_faces_name = [
    ]

dict_known_faces = {}

known_faces_path = './pics'


def create_app():
    initFaces()
    return Flask(__name__)

#########################################################################################
# Load the jpg files into arrays
#########################################################################################
def initFaces():
    if( len(known_faces) != 0):
        return

    print("Loading known faces ...")    

    start_time = time.time()  
    for filename in os.listdir(known_faces_path):
        if filename.endswith(".png") or filename.endswith(".jpg"): 
            print(os.path.join(known_faces_path, filename ))

            load_image = face_recognition.load_image_file( os.path.join(known_faces_path, filename) )
            load_image_encoding = face_recognition.face_encodings(load_image)[0]
            known_faces_name.append( os.path.splitext(filename)[0] )
            known_faces.append(load_image_encoding)
            dict_known_faces[ os.path.splitext(filename)[0] ] = load_image_encoding

            continue
        else:
            continue

    print("--- %s seconds ---" % (time.time() - start_time))

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

    # dict_known_faces["biden"] = biden_face_encoding
    # dict_known_faces["obama"] = obama_face_encoding
    # dict_known_faces["litingjun"] = litingjun_face_encoding
#########################################################################################


app = create_app()


def detect_faces_in_image(file_stream):

    face_found = False
    start_time = time.time()

    # Load the uploaded image file
    unknown_image = face_recognition.load_image_file(file_stream)
    # print(unknown_image)
    try:
        # Get face encodings for any faces in the uploaded image
        unknown_face_encodings = face_recognition.face_encodings(unknown_image)
        # print(unknown_face_encodings)
        unknown_face_encoding = unknown_face_encodings[0]
        # print(unknown_face_encoding)
        results = face_recognition.compare_faces(known_faces, unknown_face_encoding)
        print results
        
        if (not True in results):
            print("该图片没有在我们的人脸库中")

        i = 0
        for result in results:
            
            if result and known_faces_name[i] != "tmp": 
                face_found = True
                username = known_faces_name[i]           

            i = i+1

        print("--- Found user in %s seconds ---" % (time.time() - start_time))

    except IndexError:
        print("该图片没有在我们的人脸库中，请重新拍摄")
    

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



@app.route('/face/image/match2', methods=['POST'])
def match2():
    
    ######################################## check ######################################## 
    if not request.json or not 'format' in request.json:
        format = "png"
    
    if not request.json or not 'groupid' in request.json:
        groupid = "yunnanca:tech"

    if not request.json or not 'top' in request.json:
        top = 1
    #########################################################################################

    if not request.json or not 'data' in request.json:
        abort(400)
    task = {
        'data': request.json['data'],
        'description': request.json.get('description', ""),
        'done': False
    }

    imgdata = base64.b64decode( request.json['data'] )
    file_stream = 'tmp.jpg'  # I assume you have a way of picking unique filenames
    with open(file_stream, 'wb') as f:
        f.write(imgdata)

    # return jsonify({'task': task}), 201
    return compare_faces_with_image(file_stream, request.json['username'])


@app.route('/face/image/match', methods=['POST'])
def match():

    ######################################## check ######################################## 
    if not request.json or not 'format' in request.json:
        format = "png"
    
    if not request.json or not 'groupid' in request.json:
        groupid = "yunnanca:tech"

    if not request.json or not 'top' in request.json:
        top = 1
    #########################################################################################    

    # $ curl -XPOST -F "file=@obama2.jpg" http://192.168.10.10:5001/face/image/matchN
    # Check if a valid image file was uploaded
    if request.method == 'POST':
        if 'file' in request.files:            
            file_stream = request.files['file']

            if file_stream.filename == '':
                return redirect(request.url)

            if file_stream and allowed_file(file_stream.filename):
              
                # The image file seems valid! Detect faces and return the result.
                return compare_faces_with_image(file_stream, file_stream.filename)
        else:
            print "check Http Body"


    if not request.json or not 'data' in request.json:
        abort(400)
    task = {
        'data': request.json['data'],        
    }
    # print request.json['data']

    # For data is Base64
    imgdata = base64.b64decode( request.json['data'] )
    
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.jpg'  # I assume you have a way of picking unique filenames
    print filename
    with open(filename, 'wb') as f:
        f.write(imgdata)

    return detect_faces_in_image(filename)






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


def compare_faces_with_image(file_stream, username):  

    try:
        process_username = os.path.splitext(username)[0]

        # print('file_stream')
        # print file_stream
        # print('username='+username)

        start_time = time.time()

        # Load the uploaded image file
        img = face_recognition.load_image_file(file_stream)
        print("--- load_image_file file_stream " + file_stream.filename + " in %s seconds ---" % (time.time() - start_time))

        start_time = time.time()
        # Get face encodings for any faces in the uploaded image
        unknown_face_encodings = face_recognition.face_encodings(img)
        print("--- face_encodings in %s seconds ---" % (time.time() - start_time))

        print os.path.dirname(os.path.abspath(__file__))

        start_time = time.time()
        # Load the jpg files into numpy arrays
        file_path = os.path.join(known_faces_path, process_username + ".jpg")

        username_image = face_recognition.load_image_file( file_path )
        print("--- load_image_file " + file_path + " in %s seconds ---" % (time.time() - start_time))

        start_time = time.time()
        username_face_encoding = face_recognition.face_encodings(username_image)[0]
        print("--- face_encodings in %s seconds ---" % (time.time() - start_time))

        unknown_face_encoding = unknown_face_encodings[0]

        known_faces = [
            username_face_encoding,
        ]

        start_time = time.time()
        results = face_recognition.compare_faces(known_faces, unknown_face_encoding)
        print("--- compare_faces in %s seconds ---" % (time.time() - start_time))

        face_found = True

        if ( results[0] ):
            username = username
        else:
            face_found = False

        print("--- Found user in %s seconds ---" % (time.time() - start_time))
    except IndexError:
        face_found = False   
    except IOError:
        result = {
            "info": "user " + process_username +" not found"
        }
        return jsonify(result)

    # Return the result as json
    if ( face_found ):
        result = {
            "username": process_username,
            "info": "success",       
        }
    else:
        result = {
            "info": "failed"
        }
    
    
    return jsonify(result)






if __name__ == "__main__":


    app.run(host='0.0.0.0', port=5001, debug=True)
