import face_recognition as fr
import numpy as np
from flask import Flask, request, jsonify
from flask_ngrok import run_with_ngrok

import model

app = Flask(__name__)
app.config["DEBUG"] = True
run_with_ngrok(app)

dbname = 'face_db'
password = 'AdminPass123'
db = model.DataBase(dbname, password)


def res_cors(data):
    res = jsonify(data)
    res.headers.add("Access-Control-Allow-Origin", "*")
    return res


def check(data, img, tol=0.6):
    face_locations = fr.face_locations(img)
    ids = set()
    if len(face_locations):
        face_encodings = fr.face_encodings(img, face_locations)

        for face_encoding in face_encodings:
            matches = fr.compare_faces(data, face_encoding, tol)
            face_distances = fr.face_distance(data, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                ids.add(ids[best_match_index])

    return ids


@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def home():
    data = {
        'args': str(request.args),
        'header': str(request.headers),
        'form': str(request.form),
        'files': str(request.files),
        'json': str(request.json),
        'values': str(request.values),
        'data': str(request.data)
    }
    return res_cors(data)


@app.route('/api/users', methods=['GET'])
def get_faces():
    return res_cors(db.find_all())


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_face(user_id):
    return res_cors(db.find(user_id))


@app.route('/api/users', methods=['POST'])
def insert_face():
    if not request.form or 'id' not in request.form or 'file' not in request.files:
        return res_cors({'error': 'Bad request'}), 400

    users = db.get_data()
    face_id = request.form['id']

    if face_id in users['id']:
        return res_cors({'error': 'ID exist'}), 400

    data = []
    for file in request.files.getlist('file'):
        img = fr.load_image_file(file)
        embeds = fr.face_encodings(img)
        if len(embeds) == 0:
            return res_cors({'error': 'Face not found'}), 400

        if len(check(users['data'], embeds[0])) > 0:
            return res_cors({'error': 'Face exist'}), 400

        if len(data) > 0 and len(check(data, embeds[0])) == 0:
            return res_cors({'error': 'Different faces in file'}), 400

        data.append(embeds[0])

    user = {
        'id': face_id,
        'data': data
    }
    if db.insert(user):
        user.pop('_id', None)
        return res_cors(user), 201

    return res_cors({'error': 'Database error'}), 500


@app.route('/api/users', methods=['DELETE'])
def remove_face():
    if not request.form or 'id' not in request.form:
        return res_cors({'error': 'Bad request'}), 400

    user_id = request.form['id']
    if not db.find(user_id):
        return res_cors({'error': 'ID not exist'}), 400

    if db.remove(user_id):
        return res_cors({'id': user_id}), 200

    return res_cors({'error': 'Database error'}), 500


@app.route('/api/users/check', methods=['POST'])
def check_face():
    users = db.get_data()
    if len(users) == 0:
        return res_cors({'error': 'No user in database'}), 200

    if not request.form or 'file' not in request.files:
        return res_cors({'error': 'Bad request'}), 400
    if 'tol' not in request.form:
        return res_cors({'error': 'Bad request'}), 400

    tol = float(request.form['tol'])
    file = request.files['file']
    img = fr.load_image_file(file)

    ids = check(users['data'], img, tol)
    return res_cors(users['id'][ids]), 200


@app.errorhandler(404)
def page_not_found():
    return res_cors({'error': 'Not found'}), 404


app.run()
