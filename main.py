from face_model.model_dlib import Model
from utilities import *
from flask import Flask, request, jsonify
from flask_ngrok import run_with_ngrok
import os
import shutil
from database import DataBase
import logging

# Users database
dbname = 'face_db'
password = 'AdminPass123'
cluster = 'cluster0.qe6sa.mongodb.net'
db = DataBase(dbname, password, cluster)

# Model
TOL = 0.46
model = Model()

if not os.path.isdir('data'):
    os.mkdir('data')

app = Flask(__name__, static_url_path='/data', static_folder='data')
app.config["DEBUG"] = False


# Add CORS to response header
def res_cors(key, val):
    status = 'success' if key != 'error' else 'failed'
    data = {
        'status': status,
        key: val
    }
    res = jsonify(data)
    res.headers.add("Access-Control-Allow-Origin", "*")
    return res


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
def get_users():
    try:
        limit = 0 if 'limit' not in request.args else request.args['limit']
        offset = 0 if 'offset' not in request.args else request.args['offset']

        users, sz = db.find_all(limit, offset)

        if sz != 0:
            return res_cors('users', users), 200

        return res_cors('error', 'No user in database'), 200
    except Exception as ex:
        logging.exception("message")
        print(ex)
        return res_cors('error', 'Database error'), 500


@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = db.find(user_id)

        if user:
            return res_cors('user', user), 200

        return res_cors('error', 'User id not exist'), 200
    except Exception as ex:
        logging.exception("message")
        print(ex)
        return res_cors('error', 'Database error'), 500


@app.route('/api/user', methods=['POST'])
def insert_face():
    try:
        if not request.form:
            return res_cors('error', 'Bad request'), 400

        if 'id' not in request.form:
            return res_cors('error', 'No "id" in form'), 200

        if 'file' not in request.files:
            return res_cors('error', 'No "file" in form'), 200

        user = {'id': int(request.form['id'])}
        # Check user exist
        if db.find(user['id']):
            return res_cors('error', 'ID exist'), 200

        data = []
        images = []
        for file in request.files.getlist('file'):
            img = load_img(file)
            # Get face embed
            embeds = model.get_embed(img)

            if len(embeds) == 0:
                return res_cors('error', 'Face not found'), 200

            data.append(embeds[0])
            images.append(img)

        # Check photo same person
        if any(distance(data[0], data[1:]) > TOL):
            return res_cors('error', 'Different faces in file'), 200

        # Get mean embeds
        user['embed'] = mean(data)

        db_id, db_embed, sz = db.get_users()

        # Check embeds exist
        if sz != 0:
            idx, dist = find_min(user['embed'], db_embed)
            if dist <= TOL:
                return res_cors('error', 'Face exist'), 200

        # Save photo folder
        user_path = f'data/{user["id"]}'
        user['photo'] = save_photo(user_path, images, request.host)

        # Insert user to database
        user['embed'] = user['embed'].tolist()
        if db.insert(user):
            user.pop('_id', None)
            return res_cors('user', user), 201
        else:
            shutil.rmtree(user_path)

        return res_cors('error', 'Database error'), 500
    except Exception as ex:
        logging.exception("message")
        print(ex)
        return res_cors('error', 'Something wrong'), 500


@app.route('/api/user/<int:user_id>', methods=['DELETE'])
def remove_face(user_id):
    try:
        user_id = user_id

        if not db.find(user_id):
            return res_cors('error', 'ID not exist'), 400

        if db.remove(user_id):
            try:
                shutil.rmtree(f'data/{user_id}')
            except Exception as ex:
                print(ex)

            return res_cors('id', user_id), 200

        return res_cors('error', 'Database error'), 500
    except Exception as ex:
        logging.exception("message")
        print(ex)
        return res_cors('error', 'Something wrong'), 500


@app.route('/api/check', methods=['POST'])
def check_face():
    try:
        id_list, embed_list, sz = db.get_users()

        if sz == 0:
            return res_cors('error', 'No user in database'), 200

        if 'file' not in request.files:
            return res_cors('error', 'Bad request'), 400

        file = request.files['file']
        img = load_img(file)
        embeds = model.get_embed(img)
        if len(embeds) == 0:
            return res_cors('error', 'Face not found'), 400

        ids = []
        for embed in embeds:
            idx, dist = find_min(embed, embed_list)
            if dist <= TOL:
                ids.append(idx)

        return res_cors('users', id_list[ids].tolist()), 200
    except Exception as ex:
        logging.exception("message")
        print(ex)
        return res_cors('error', 'Something wrong'), 500


@app.errorhandler(404)
def page_not_found(e):
    return res_cors('error', 'Not found'), 404


def main():
    run_with_ngrok(app)
    app.run()


if __name__ == '__main__':
    main()
