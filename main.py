from face_model.model_dlib import Model
from utilities import *
from flask import Flask, request
from flask_ngrok import run_with_ngrok
from database import DataBase
import logging
import argparse
#import requests


app = Flask(__name__, static_url_path='/data', static_folder='data')

# Users database
db_name = 'face_db'
db_pass = 'AdminPass123'
cluster = 'cluster0.qe6sa.mongodb.net'

db = DataBase(app, db_name, db_pass, cluster)
model = Model()


@app.route('/login', methods=['POST'])
def login():
    try:
        if 'username' not in request.form:
            return res_cors({'error': 'No username in form'}), 400
        if 'password' not in request.form:
            return res_cors({'error': 'No password in form'}), 400

        username = request.form['username']
        password = request.form['password']

        '''
        url = 'http://localhost/login/token.php'
        service = 'moodle_mobile_app'

        r = requests.post(f'{url}?username={userID}&password={password}&service={service}')

        result = r.json()
        if r.status_code == 200 and 'token' in result:
            return res_cors({'token': result['token']}), 200
        '''

        if username == 'admin' and password == 'admin':
            return res_cors({'token': 'admin', 'role': 0}), 200

        if username == 'teacher' and password == 'teacher':
            return res_cors({'token': 'teacher', 'role': 1}), 200

        return res_cors({'error': 'Wrong username or password'}), 401

    except Exception as ex:
        logging.exception("message")
        print(ex)
        return res_cors({'error': 'Error'}), 500


@app.route('/face/users', methods=['GET'])
def get_users():
    try:
        ids, _ = db.get_users()

        if len(ids) != 0:
            return res_cors({'users': ids}), 200

        return res_cors({'error': 'No user in database'}), 200
    except Exception as ex:
        logging.exception("message")
        print(ex)
        return res_cors({'error': 'Database error'}), 500


@app.route('/face/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = db.get_user(user_id)

        if user:
            return res_cors({'user': 'Exist'}), 200

        return res_cors({'error': 'User not exist'}), 404
    except Exception as ex:
        logging.exception("message")
        print(ex)
        return res_cors({'error': 'Database error'}), 500


@app.route('/face/user', methods=['POST'])
def insert():
    try:
        if not request.form:
            return res_cors({'error': 'Bad request'}), 400

        if 'id' not in request.form:
            return res_cors({'error': 'No ID'}), 400

        if 'image' not in request.files:
            return res_cors({'error': 'No image'}), 400

        user = {
            'id': int(request.form['id']),
            'embeds': []
        }
        db_ids, db_embeds = db.get_users()
        # Check user exist
        if user['id'] in db_ids:
            return res_cors({'error': 'ID exist'}), 200

        embeds = []
        for file in request.files.getlist('image'):
            img = load_img(file)
            # Check image size
            if img.shape != model.size:
                return res_cors({'error': f'Image size {model.size}x{model.size}'}), 200

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
                return res_cors({'error': 'Face exist'}), 200

        # Insert user to database
        user['embed'] = user['embed'].tolist()
        if db.insert(user):
            return res_cors({'user': 'Added'}), 201

        return res_cors({'error': 'Database error'}), 500
    except Exception as ex:
        logging.exception("message")
        print(ex)
        return res_cors({'error': 'Error'}), 500


@app.route('/face/user/<int:user_id>', methods=['PUT'])
def update(user_id):
    try:
        if 'image' not in request.files:
            return res_cors({'error': 'No image'}), 400

        user = {
            'id': user_id,
            'embeds': []
        }
        db_ids, db_embeds = db.get_users()
        # Check user exist
        if user['id'] not in db_ids:
            return res_cors({'error': 'ID not exist'}), 404

        embeds = []
        for file in request.files.getlist('image'):
            img = load_img(file)
            # Check image size
            if img.shape != model.size:
                return res_cors({'error': f'Image size {model.size}x{model.size}'}), 200

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
                return res_cors({'error': 'Face exist'}), 200

        # Insert user to database
        user['embed'] = user['embed'].tolist()
        if db.update(user):
            return res_cors({'user': 'Updated'}), 200

        return res_cors({'error': 'Database error'}), 500
    except Exception as ex:
        logging.exception("message")
        print(ex)
        return res_cors({'error': 'Error'}), 500


@app.route('/face/user/<int:user_id>', methods=['DELETE'])
def remove(user_id):
    try:
        ids, _ = db.get_users()
        if user_id not in ids:
            return res_cors({'error': 'ID not exist'}), 400

        if db.remove(user_id):
            return res_cors({'user': 'Removed'}), 200

        return res_cors({'error': 'Database error'}), 500
    except Exception as ex:
        logging.exception("message")
        print(ex)
        return res_cors({'error': 'Error'}), 500


@app.route('/check', methods=['POST'])
def manual_check():
    try:
        if 'id' not in request.args:
            return res_cors({'error': 'Bad request'}), 400

        idx = request.args['id']
        if idx not in ['1', '2', '3']:
            return res_cors({'error': 'Class ID not exist'}), 404

        if 'date' not in request.args:
            return res_cors({'error': 'Bad request'}), 400

        if 'token' not in request.args:
            return res_cors({'error': 'Bad request'}), 400

        token = request.args['token']
        if token != 'teacher' and token != 'admin':
            return res_cors({'error': 'Invalid token'}), 401

        if 'users' not in request.json:
            return res_cors({'error': 'No user in request'}), 400

        ids = ['1', '2', '3', '4', '5']
        users = request.json['users']
        for user in users:
            if user['id'] not in ids:
                return res_cors({'error': 'User not exist'}), 400

        return res_cors({'users': 'Checked'}), 200
    except Exception as ex:
        logging.exception("message")
        print(ex)
        return res_cors({'error': 'Error'}), 500


@app.route('/face/check', methods=['POST'])
def check():
    try:
        if 'id' not in request.args:
            return res_cors({'error': 'Bad request'}), 400

        idx = request.args['id']
        if idx not in ['1', '2', '3']:
            return res_cors({'error': 'Class ID not exist'}), 404

        if 'date' not in request.args:
            return res_cors({'error': 'Bad request'}), 400

        if 'token' not in request.args:
            return res_cors({'error': 'Bad request'}), 400

        token = request.args['token']
        if token != 'teacher' and token != 'admin':
            return res_cors({'error': 'Invalid token'}), 401

        if 'image' not in request.files:
            return res_cors({'error': 'No image'}), 400

        db_ids, db_embeds = db.get_users()
        if not db_ids:
            return res_cors({'error': 'No user in database'}), 200

        db_embeds = np.array(db_embeds)

        users = []
        for file in request.files.getlist('image'):
            img = load_img(file)

            # Check image size
            if img.shape != model.size:
                return res_cors({'error': f'Image size {model.size}'}), 200

            embed = model.get_embed(img)

            idx, dist = find_min(embed, db_embeds)
            if dist <= model.tol:
                users.append(
                    {
                        'id': db_ids[idx],
                        'name': f'a{db_ids[idx]}'
                    }
                )

        return res_cors({'users': users}), 200
    except Exception as ex:
        logging.exception("message")
        print(ex)
        return res_cors({'error': 'Error'}), 500


@app.errorhandler(404)
def page_not_found(e):
    print(e)
    return res_cors({'error': 'Not found'}), 404


def main(argv):
    if 'remote' in argv and argv.remote == '1':
        app.config["DEBUG"] = False
        run_with_ngrok(app)
    else:
        app.config["DEBUG"] = True

    app.run()


if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('--remote', type=str, default='0')
    args = parse.parse_args()
    main(args)
