from flask import Flask, request, jsonify
import face_recognition as fr
import numpy as np
from flask_ngrok import run_with_ngrok
import model


app = Flask(__name__)
app.config["DEBUG"] = True
run_with_ngrok(app)

dbname = 'face_db'
password = 'AdminPass123'
db = model.DataBase(dbname, password)


@app.route('/', methods=['GET'])
def home():
    return ''


@app.route('/api/faces', methods=['GET'])
def get_faces():
    faces = db.find_all()
    return jsonify(faces)


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

    file = request.files['file']
    img = fr.load_image_file(file)
    data = fr.face_encodings(img)
    if len(data) == 0:
        return jsonify({'error': 'Face not found'}), 400

    face = {
        'id': face_id,
        'data': data[0].tolist()
    }
    if db.insert(face):
        face.pop('_id', None)
        return jsonify(face), 201

    return jsonify({'error': 'Database error'}), 500


@app.route('/api/faces', methods=['PUT'])
def update_face():
    if not request.form or 'file' not in request.files or 'face_id' not in request.form:
        return jsonify({'error': 'Bad request'}), 400

    face_id = request.form['id']
    if not db.find(face_id):
        return jsonify({'error': 'ID not exist'}), 400

    file = request.files['file']
    img = fr.load_image_file(file)
    data = fr.face_encodings(img)
    if len(data) == 0:
        return jsonify({'error': 'Face not found'}), 400

    face = {
        'id': face_id,
        'data': data
    }
    if db.update(face):
        return jsonify(face), 200

    return jsonify({'error': 'Database error'}), 500


@app.route('/api/faces', methods=['DELETE'])
def remove_face():
    if not request.form or 'face_id' not in request.form:
        return jsonify({'error': 'Bad request'}), 400

    face_id = request.form['id']
    if not db.find(face_id):
        return jsonify({'error': 'ID not exist'}), 400

    if db.remove()(face_id):
        return jsonify({'id': face_id}), 200

    return jsonify({'error': 'Database error'}), 500


def check(faces, img, tol):
    faces_id = [face['id'] for face in faces]
    faces_data = [face['data'] for face in faces]

    face_locations = fr.face_locations(img)
    ids = []
    if len(face_locations):
        face_encodings = fr.face_encodings(img, face_locations)

        for face_encoding in face_encodings:
            matches = fr.compare_faces(faces_data, face_encoding, tol)
            face_distances = fr.face_distance(faces_data, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                ids.append(faces_id[best_match_index])

    return jsonify({'ids': ids}), 200


@app.route('/api/faces/check', methods=['POST'])
def check_face():
    if not request.form or 'file' not in request.files:
        return jsonify({'error': 'Bad request'}), 400
    if 'tol' not in request.form:
        return jsonify({'error': 'Bad request'}), 400

    tol = float(request.form['tol'])
    file = request.files['file']
    img = fr.load_image_file(file)

    faces = db.find_all()
    if len(faces):
        return check(faces, img, tol)

    return jsonify({'error': 'Database error'}), 500


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': 'Not found'}), 404


app.run()
