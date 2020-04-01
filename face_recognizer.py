import responder
from marshmallow import Schema, fields, ValidationError

import numpy as np
import os
import face_recognition
from PIL import Image
from io import BytesIO

# function to load image
def load_image(file, mode='RGB'):
    image = Image.open(file)
    if mode:
        image = image.convert(mode)
    return image

# function to cal face image encoding
def cal_face_encoding(file, mode='RGB',find_face_location=True):
    try:
        image = load_image(file)
        image = np.array(image)
        if find_face_location:
            face_locations = face_recognition.face_locations(image)
            face_encoding = face_recognition.face_encodings(image,face_locations)[0]
        else:
            face_encoding = face_recognition.face_encodings(image)[0]
        return face_encoding
    except Exception as e:
        print("Error at cal_face_encoding")
        print(e)
        return None

# get file paths
SAMPLE_IMAGE_DIR = "./images/sample"
sample_images = os.listdir(SAMPLE_IMAGE_DIR)

# set empty name list & empty encoding list
sample_names = []
sample_face_encoding_list = np.random.random((len(sample_images), 128)).astype('float32')

# get sample encoding
for i, filename in enumerate(sample_images):
    face_encoding = cal_face_encoding(os.path.join(SAMPLE_IMAGE_DIR,filename))
    sample_face_encoding_list[i] = face_encoding
    sample_names.append(os.path.splitext(filename)[0])

print("setup samples done")

api = responder.API(
    openapi='3.0.0',  # OpenAPI version
    docs_route='/docs',  # endpoint for interactive documentation by swagger UI. if None, this is not available.
)

@api.route("/")
async def view(req, resp):
    resp.media = {'success': True}

@api.route("/recognizer")
async def recognizer(req, resp):
    if req.method == 'get':
        # return form to upload an image you want to recognize
        # resp.status_code = 404
        resp.content = api.template('recognizer.html', message="Please upload IMAGE.")
    if req.method == 'post':
        try:
            global sample_face_encoding_list
            # return recognized name
            data = await req.media(format="files")
            test_face_encoding = cal_face_encoding(BytesIO(data["file"]['content']))
            if test_face_encoding is None:
                resp.media = {'success': False, 'Error': "This image is not available."}
                return
            name = "Unknown"
            tolerance = 0.4
            face_distances = face_recognition.face_distance(sample_face_encoding_list, test_face_encoding)
            matches = list(face_distances <= tolerance)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = sample_names[best_match_index]
            resp.media = {'name': name, 'success': True}
        except Exception as e:
            print("Error at recognizer")
            print(e)
            resp.media = {'success': False, 'Error':e}
        # resp.content = api.template('recognizer.html', message="It's {}!".format(name))

@api.route("/register")
async def register(req, resp):
    if req.method == 'get':
        # return form to upload an image you want to recognize
        # resp.status_code = 404
        resp.content = api.template('register.html', message="Please enter NAME and upload his or her IMAGE.")
    if req.method == 'post':
        try:
            global sample_face_encoding_list
            # return recognized name
            data = await req.media(format="files")
            name = data["name"].decode('utf-8')
            print(name)
            image = load_image(BytesIO(data["file"]['content']))
            # save image
            new_image_path = os.path.join(SAMPLE_IMAGE_DIR,'{}.jpg'.format(name))
            image.save(new_image_path, quality=95)
            # set encoding
            face_encoding = cal_face_encoding(new_image_path)
            if face_encoding is None:
                os.remove(new_image_path)
                resp.media = {'Error': "This image is not available."}
                return
            sample_face_encoding_list = np.append(sample_face_encoding_list, face_encoding.reshape(1, -1), axis=0)
            # set name
            sample_names.append(name)
            resp.media = {'success': True}
        except Exception as e:
            print("Error at register")
            print(e)
            resp.media = {'success': False, 'Error':e}
        # resp.content = api.template('index.html', message="It's {}!".format(name))

if __name__ == "__main__":
    api.run()