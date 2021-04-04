from face_service.api import FaceAPI
from photo_service.api import PhotoApi
from flask import Blueprint, request
from moodle_service import *


def create_face_bp(app):
    face_api = FaceAPI(app)
    photo_api = PhotoApi(app)
    face_bp = Blueprint('face_bp', __name__)

    @face_bp.route('/', methods=['GET'])
    def get_users():
        try:
            v = verify(request.args)
            if v:
                return v

            code, result = face_api.get_users()

            if code == 200:
                return res_cors({
                    'status': code,
                    'message': 'Successful',
                    'data': result
                }), code

            return res_cors({
                'status': code,
                'message': result,
                'data': ''
            }), code
        except Exception as ex:
            print(f'\n***FACE Get_users error: {ex}***\n')
            return res_cors({
                'status': 500,
                'message': str(ex),
                'data': ''
            }), 500

    @face_bp.route('/<username>', methods=['GET'])
    def get_user(username):
        try:
            v = verify(request.args)
            if v:
                return v

            code, result = face_api.get_user(username)

            if code == 200:
                code, result = photo_api.get_user(username)
                data = {
                    'left': result['left'],
                    'right': result['right'],
                    'front': result['front']
                }

                return res_cors({
                    'status': 200,
                    'message': 'Successful',
                    'data': data
                }), 200

            return res_cors({
                'status': 404,
                'message': result,
                'data': ''
            }), 404
        except Exception as ex:
            print(f'\n***FACE Get_user error: {ex}***\n')
            return res_cors({
                'status': 500,
                'message': str(ex),
                'data': ''
            }), 500

    @face_bp.route('/<username>', methods=['POST'])
    def insert(username):
        try:
            v = verify(request.args, admin=True)
            if v:
                return v

            if 'front' not in request.form:
                return res_cors({
                    'status': 400,
                    'message': 'Missing "front"',
                    'data': request.form
                }), 400
            if 'left' not in request.form:
                return res_cors({
                    'status': 400,
                    'message': 'Missing "left"',
                    'data': ''
                }), 400
            if 'right' not in request.form:
                return res_cors({
                    'status': 400,
                    'message': 'Missing "right"',
                    'data': ''
                }), 400

            if not moodle_user(username):
                return res_cors({
                    'status': 404,
                    'message': 'Username not found',
                    'data': ''
                }), 404

            front = load_img(request.form['front'])
            left = load_img(request.form['left'])
            right = load_img(request.form['right'])

            code, result = face_api.create_user(username, front, left, right)

            if code == 201:
                code, result = photo_api.create_user(
                    username,
                    left=request.form['left'],
                    right=request.form['right'],
                    front=request.form['front']
                )
                if code != 200:
                    face_api.remove_user(username)

            return res_cors({
                'status': code,
                'message': result,
                'data': ''
            }), code
        except Exception as ex:
            if face_api.get_user(username):
                face_api.remove_user(username)

            print(f'\n***FACE Insert_users error: {ex}***\n')
            return res_cors({
                'status': 500,
                'message': str(ex),
                'data': ''
            }), 500

    @face_bp.route('/<username>', methods=['PUT'])
    def update(username):
        try:
            v = verify(request.args, admin=True)
            if v:
                return v

            if 'front' not in request.form:
                return res_cors({
                    'status': 400,
                    'message': 'Missing "front"',
                    'data': ''
                }), 400
            if 'left' not in request.form:
                return res_cors({
                    'status': 400,
                    'message': 'Missing "left"',
                    'data': ''
                }), 400
            if 'right' not in request.form:
                return res_cors({
                    'status': 400,
                    'message': 'Missing "right"',
                    'data': ''
                }), 400

            front = load_img(request.form['front'])
            left = load_img(request.form['left'])
            right = load_img(request.form['right'])
            code, result = face_api.update_user(username, front, left, right)

            if code == 200:
                code, result = photo_api.update_user(
                    username,
                    left=request.form['left'],
                    right=request.form['right'],
                    front=request.form['front']
                )

            return res_cors({
                'status': code,
                'message': result,
                'data': ''
            }), code
        except Exception as ex:
            print(f'\n***FACE Update_users error: {ex}***\n')
            return res_cors({
                'status': 500,
                'message': str(ex),
                'data': ''
            }), 500

    @face_bp.route('/<username>', methods=['DELETE'])
    def remove(username):
        try:
            v = verify(request.args, admin=True)
            if v:
                return v

            code, result = face_api.remove_user(username)

            if code == 200:
                code, result = photo_api.remove_user(username)

            return res_cors({
                'status': code,
                'message': result,
                'data': ''
            }), code
        except Exception as ex:
            print(f'\n***FACE Remove_users error: {ex}***\n')
            return res_cors({
                'status': 500,
                'message': str(ex),
                'data': ''
            }), 500

    @face_bp.route('/checkin/<session_id>', methods=['POST'])
    def check(session_id):
        try:
            v = verify(request.args)
            if v:
                return v

            if 'image' not in request.form:
                return res_cors({
                    'status': 400,
                    'message': 'Missing "image"',
                    'data': ''
                }), 400

            users = []
            for image in request.form.getlist('image'):
                img = load_img(image)

                code, username = face_api.verify(img)
                if code != 200:
                    continue

                if not moodle_checkin(session_id, username, 1):
                    continue

                user = moodle_user(username)

                if user:
                    code, result = photo_api.get_user(username)
                    if code == 200:
                        user['avatar'] = result['front']

                    users.append(user)

            return res_cors({
                'status': 200,
                'message': 'Successful',
                'data': users
            }), 200
        except Exception as ex:
            print(f'\n***FACE Check_user error: {ex}***\n')
            return res_cors({
                'status': 500,
                'message': str(ex),
                'data': ''
            }), 500

    return face_bp
