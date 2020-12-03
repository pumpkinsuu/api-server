from flask import Flask, request, jsonify
import face_recognition as fr
from flask import json
import numpy as np
from flask_ngrok import run_with_ngrok
import model


app = Flask(__name__)
app.config["DEBUG"] = True
run_with_ngrok(app)

dbname = 'face_db'
password = 'AdminPass123'
db = model.DataBase(dbname, password)


@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def home():
    data = {
        'args': str(request.args),
        'header': str(request.headers),
        'form': str(request.form),
        'files': str(request.files),
        'json': str(request.json),
        'values': str(request.values)
    }
    return jsonify(data)


@app.route('/api/faces', methods=['GET'])
def get_faces():
    ids, data = db.find_all()
    return jsonify(zip(ids, data))


@app.route('/api/faces/<int:face_id>', methods=['GET'])
def get_face(face_id):
    face = db.find(face_id)
    return jsonify(face)


@app.route('/api/faces', methods=['POST'])
def insert_face():
    if not request.form or 'id' not in request.form or 'file' not in request.files:
        return jsonify({'error': 'Bad request'}), 400

    face_id = request.form['id']
    if db.find(face_id):
        return jsonify({'error': 'ID exist'}), 400

    data = []
    for file in request.files.getlist('file'):
        img = fr.load_image_file(file)
        faces = fr.face_encodings(img)
        if len(faces) == 0:
            return jsonify({'error': 'Face not found'}), 400
        data.append(faces[0])

    face = {
        'id': face_id,
        'data': data
    }
    if db.insert(face):
        face.pop('_id', None)
        return jsonify(face), 201

    return jsonify({'error': 'Database error'}), 500


@app.route('/api/faces', methods=['DELETE'])
def remove_face():
    if not request.form or 'id' not in request.form:
        return jsonify({'error': 'Bad request'}), 400

    face_id = request.form['id']
    if not db.find(face_id):
        return jsonify({'error': 'ID not exist'}), 400

    if db.remove(face_id):
        return jsonify({'id': face_id}), 200

    return jsonify({'error': 'Database error'}), 500


def check(ids, data, img, tol):
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

    return jsonify({'ids': ids}), 200


@app.route('/api/faces/check', methods=['POST'])
def check_face():
    ids, data = db.find_all()
    if len(ids) == 0:
        return jsonify({'error': 'No faces in database'}), 200

    if not request.form or 'file' not in request.files:
        return jsonify({'error': 'Bad request'}), 400
    if 'tol' not in request.form:
        return jsonify({'error': 'Bad request'}), 400

    tol = float(request.form['tol'])
    file = request.files['file']
    img = fr.load_image_file(file)

    return check(ids, data, img, tol)


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': 'Not found'}), 404


app.run()
