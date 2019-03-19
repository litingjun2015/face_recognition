# This is a _very simple_ example of a web service that recognizes faces in uploaded images.
# Upload an image file and it will check if the image contains a picture of Barack Obama.
# The result is returned as json. For example:
#
# $ curl -XPOST -F "file=@obama2.jpg" http://127.0.0.1:5001
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

# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/face/image/matchN', methods=['POST'])
def matchN():
    if not request.json or not 'data' in request.json:
        abort(400)
    task = {
        'data': request.json['data'],
    }

    imgdata = base64.b64decode( request.json['data'] )
    filename = 'tmp.jpg'  # I assume you have a way of picking unique filenames
    with open(filename, 'wb') as f:
        f.write(imgdata)

    # return jsonify({'task': task}), 201
    return detect_faces_in_image(filename)


@app.route('/face/image/match', methods=['POST'])
def match():
    if not request.json or not 'data' in request.json:
        abort(400)
    task = {
        'data': request.json['data'],
        'description': request.json.get('description', ""),
        'done': False
    }

    imgdata = base64.b64decode( request.json['data'] )
    filename = 'tmp.jpg'  # I assume you have a way of picking unique filenames
    with open(filename, 'wb') as f:
        f.write(imgdata)

    # return jsonify({'task': task}), 201
    return compare_faces_with_image(filename, request.json['username'])



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

    # Load the uploaded image file
    img = face_recognition.load_image_file(file_stream)
    # Get face encodings for any faces in the uploaded image
    unknown_face_encodings = face_recognition.face_encodings(img)


    # Load the jpg files into numpy arrays
    username_image = face_recognition.load_image_file(username + ".jpg")

    username_face_encoding = face_recognition.face_encodings(username_image)[0]

    unknown_face_encoding = unknown_face_encodings[0]

    known_faces = [
        username_face_encoding,
    ]

    results = face_recognition.compare_faces(known_faces, unknown_face_encoding)

    face_found = True

    if ( results[0] ):
        username = username
    else:
        face_found = False

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

def detect_faces_in_image(file_stream):

    # Load the uploaded image file
    img = face_recognition.load_image_file(file_stream)
    # Get face encodings for any faces in the uploaded image
    unknown_face_encodings = face_recognition.face_encodings(img)


    # Load the jpg files into numpy arrays
    biden_image = face_recognition.load_image_file("biden.jpg")
    obama_image = face_recognition.load_image_file("obama.jpg")
    litingjun_image = face_recognition.load_image_file("litingjun.jpg")
    # unknown_image = face_recognition.load_image_file("obama2.jpg")

    biden_face_encoding = face_recognition.face_encodings(biden_image)[0]
    obama_face_encoding = face_recognition.face_encodings(obama_image)[0]
    litingjun_face_encoding = face_recognition.face_encodings(litingjun_image)[0]
    unknown_face_encoding = unknown_face_encodings[0]

    known_faces = [
        biden_face_encoding,
        obama_face_encoding,
        litingjun_face_encoding
    ]

    results = face_recognition.compare_faces(known_faces, unknown_face_encoding)

    face_found = True

    if ( results[0] ):
        username = "Biden"
    elif ( results[1] ):
        username = "Obama"
    elif ( results[2] ):
        username = "litingjun"
    else:
        face_found = False

    print("Is the unknown face a picture of Biden? {}".format(results[0]))
    print("Is the unknown face a picture of Obama? {}".format(results[1]))
    print("Is the unknown face a new person that we've never seen before? {}".format(not True in results))

    

    # if len(unknown_face_encodings) > 0:
    #     #  face_found = True
    #     # See if the first face in the uploaded image matches the known face of Obama
    #     match_results = face_recognition.compare_faces([known_face_encoding], unknown_face_encodings[0])
    #     if match_results[0]:
    #         is_obama = True


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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
