import face_recognition as fr
import numpy as np
from flask import Flask, request, jsonify
from flask_ngrok import run_with_ngrok
import os
import shutil
import cv2

import model


dbname = 'face_db'
password = 'AdminPass123'
cluster = 'cluster0.qe6sa.mongodb.net'
db = model.DataBase(dbname, password, cluster)

if not os.path.isdir('data'):
    os.mkdir('data')

app = Flask(__name__, static_url_path='/data', static_folder='data')
app.config["DEBUG"] = True
run_with_ngrok(app)


def res_cors(key, val):
    status = 'success' if key != 'error' else 'failed'
    data = {
        'status': status,
        key: val
    }
    res = jsonify(data)
    res.headers.add("Access-Control-Allow-Origin", "*")
    return res


def check(data, embed, tol=0.4):
    matches = fr.compare_faces(data, embed, tol)
    face_distances = fr.face_distance(data, embed)
    best_match_index = np.argmin(face_distances)
    if matches[best_match_index]:
        return best_match_index
    return ''


@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def home():
    data = {
        'host': str(request.host),
        'args': str(request.args),
        'header': str(request.headers),
        'form': str(request.form),
        'files': str(request.files),
        'json': str(request.json),
        'values': str(request.values),
        'data': str(request.data)
    }
    return res_cors('request', data)


@app.route('/api/users', methods=['GET'])
def get_faces():
    return res_cors('users', db.find_all()), 200


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_face(user_id):
    return res_cors('user', db.find(user_id)), 200


@app.route('/api/users', methods=['POST'])
def insert_face():
    if not request.form or 'id' not in request.form or 'file' not in request.files:
        return res_cors('error', 'Bad request'), 400

    data_ids, data_embeds = db.get_data()

    user_id = int(request.form['id'])

    if len(data_ids) > 0:
        if user_id in data_ids:
            return res_cors('error', 'ID exist'), 400

    data = []
    images = []
    for file in request.files.getlist('file'):
        img = fr.load_image_file(file)
        embeds = fr.face_encodings(img)
        if len(embeds) == 0:
            return res_cors('error', 'Face not found'), 400

        if len(data_ids) > 0:
            if check(data_embeds, embeds[0]) != '':
                return res_cors('error', 'Face exist'), 400

        if len(data) > 0 and check(data, embeds[0], 0.6) == '':
            return res_cors('error', 'Different faces in file'), 400

        data.append(embeds[0].tolist())
        images.append(img)

    os.mkdir(f'data/{user_id}')
    i = 1
    urls = []
    for img in images:
        cv2.imwrite(f'data/{user_id}/{i}.jpg', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        urls.append(f'http://{request.host}/data/{user_id}/{i}.jpg')
        i += 1

    user = {
        'id': user_id,
        'data': data,
        'photo': urls
    }
    if db.insert(user):
        user.pop('_id', None)
        return res_cors('user', user), 201

    return res_cors('error', 'Database error'), 500


@app.route('/api/users', methods=['DELETE'])
def remove_face():
    if not request.form or 'id' not in request.form:
        return res_cors('error', 'Bad request'), 400

    user_id = request.form['id']
    if not db.find(user_id):
        return res_cors('error', 'ID not exist'), 400

    if db.remove(user_id):
        try:
            shutil.rmtree(f'data/{user_id}')
        except Exception as ex:
            print(ex)

        return res_cors('id', user_id), 200

    return res_cors('error', 'Database error'), 500


@app.route('/api/users/check', methods=['POST'])
def check_face():
    data_ids, data_embeds = db.get_data()

    if len(data_ids) == 0:
        return res_cors('error', 'No user in database'), 200

    if 'file' not in request.files:
        return res_cors('error', 'Bad request'), 400

    tol = 0.4
    if 'tol' in request.form:
        tol = float(request.form['tol'])

    file = request.files['file']
    img = fr.load_image_file(file)
    embeds = fr.face_encodings(img)
    if len(embeds) == 0:
        return res_cors('error', 'Face not found'), 400

    ids = []
    for embed in embeds:
        ids.append(check(data_embeds, embed, tol))
    return res_cors('users', data_ids[ids].tolist()), 200


@app.errorhandler(404)
def page_not_found(e):
    return res_cors('error', 'Not found'), 404


app.run()
