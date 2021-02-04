from face_model.model_dlib import Model
from utilities import *
from flask import Flask, request, jsonify
from flask_ngrok import run_with_ngrok
from database import DataBase
import logging
import sys

app = Flask(__name__, static_url_path='/data', static_folder='data')

# Users database
dbname = 'face_db'
password = 'AdminPass123'
cluster = 'cluster0.qe6sa.mongodb.net'

db = DataBase(app, dbname, password, cluster)
model = Model()


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
        ids, _ = db.get_users()

        if len(ids) != 0:
            return res_cors('users', ids), 200

        return res_cors('error', 'No user in database'), 200
    except Exception as ex:
        logging.exception("message")
        print(ex)
        return res_cors('error', 'Database error'), 500


@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = db.get_user(user_id)

        if user:
            return res_cors('user', 'Exist'), 200

        return res_cors('error', 'User not exist'), 404
    except Exception as ex:
        logging.exception("message")
        print(ex)
        return res_cors('error', 'Database error'), 500


@app.route('/api/user', methods=['POST'])
def insert():
    try:
        if not request.form:
            return res_cors('error', 'Bad request'), 400

        if 'id' not in request.form:
            return res_cors('error', 'No ID'), 400

        if 'image' not in request.files:
            return res_cors('error', 'No image'), 400

        user = {
            'id': int(request.form['id']),
            'embeds': []
        }
        db_ids, db_embeds = db.get_users()
        # Check user exist
        if user['id'] in db_ids:
            return res_cors('error', 'ID exist'), 200

        embeds = []
        for file in request.files.getlist('image'):
            img = load_img(file)
            # Check image size
            if img.shape != model.size:
                return res_cors('error', f'Image size {model.size}x{model.size}'), 200

            # Get face embed
            embed = model.get_embed(img)
            embeds.append(embed)

        # Check same person face

        # Get mean embeds
        user['embed'] = mean(embeds)

        # Check embeds exist
        if db_embeds:
            db_embeds = np.array(db_embeds)
            idx, dist = find_min(user['embed'], db_embeds)
            if dist < model.tol:
                return res_cors('error', 'Face exist'), 200

        # Insert user to database
        user['embed'] = user['embed'].tolist()
        if db.insert(user):
            return res_cors('user', 'Added'), 201

        return res_cors('error', 'Database error'), 500
    except Exception as ex:
        logging.exception("message")
        print(ex)
        return res_cors('error', 'Error'), 500


@app.route('/api/user/<int:user_id>', methods=['PUT'])
def update(user_id):
    try:
        if 'image' not in request.files:
            return res_cors('error', 'No image'), 400

        user = {
            'id': user_id,
            'embeds': []
        }
        db_ids, db_embeds = db.get_users()
        # Check user exist
        if user['id'] not in db_ids:
            return res_cors('error', 'ID not exist'), 404

        embeds = []
        for file in request.files.getlist('image'):
            img = load_img(file)
            # Check image size
            if img.shape != model.size:
                return res_cors('error', f'Image size {model.size}x{model.size}'), 200

            # Get face embed
            embed = model.get_embed(img)
            embeds.append(embed)

        # Check same person face

        # Get mean embeds
        user['embed'] = mean(embeds)

        # Check embeds exist
        if db_embeds:
            db_embeds = np.array(db_embeds)
            idx, dist = find_min(user['embed'], db_embeds)
            if dist < model.tol and db_ids[idx] != user['id']:
                return res_cors('error', 'Face exist'), 200

        # Insert user to database
        user['embed'] = user['embed'].tolist()
        if db.update(user):
            return res_cors('user', 'Updated'), 200

        return res_cors('error', 'Database error'), 500
    except Exception as ex:
        logging.exception("message")
        print(ex)
        return res_cors('error', 'Error'), 500


@app.route('/api/user/<int:user_id>', methods=['DELETE'])
def remove(user_id):
    try:
        ids, _ = db.get_users()
        if user_id not in ids:
            return res_cors('error', 'ID not exist'), 400

        if db.remove(user_id):
            return res_cors('user', 'Removed'), 200

        return res_cors('error', 'Database error'), 500
    except Exception as ex:
        logging.exception("message")
        print(ex)
        return res_cors('error', 'Error'), 500


@app.route('/api/check', methods=['POST'])
def check():
    try:
        if 'image' not in request.files:
            return res_cors('error', 'No image'), 400

        file = request.files['image']
        img = load_img(file)

        # Check image size
        if img.shape != model.size:
            return res_cors('error', f'Image size {model.size}'), 200

        db_ids, db_embeds = db.get_users()
        if not db_ids:
            return res_cors('error', 'No user in database'), 200

        embed = model.get_embed(img)
        db_embeds = np.array(db_embeds)

        idx, dist = find_min(embed, db_embeds)
        if dist <= model.tol:
            return res_cors('user', db_ids[idx]), 200

        return res_cors('error', 'Face not exist'), 200
    except Exception as ex:
        logging.exception("message")
        print(ex)
        return res_cors('error', 'Error'), 500


@app.errorhandler(404)
def page_not_found(e):
    return res_cors('error', 'Not found'), 404


def main(argv):
    app.config["DEBUG"] = False

    if len(argv) and argv == 'remote':
        run_with_ngrok(app)

    app.run()


if __name__ == '__main__':
    main(sys.argv[1:])
