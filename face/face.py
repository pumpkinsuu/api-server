from face_service.api import FaceAPI
from flask import Blueprint, request
import os
from moodle_service import *


def create_face_bp(app):
    face_api = FaceAPI(app)
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
                    'code': code,
                    'message': 'Successful',
                    'data': result
                }), code

            return res_cors({
                'code': code,
                'message': result,
                'data': ''
            }), code
        except Exception as ex:
            print(f'\n***FACE Get_users error: {ex}***\n')
            return res_cors({
                'code': 500,
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
                return res_cors({
                    'front': f'data/{username}_front.jpg',
                    'left': f'data/{username}_left.jpg',
                    'right': f'data/{username}_right.jpg'
                }), 200

            return res_cors({
                'code': 404,
                'message': 'Not found',
                'data': ''
            }), 404
        except Exception as ex:
            print(f'\n***FACE Get_user error: {ex}***\n')
            return res_cors({
                'code': 500,
                'message': str(ex),
                'data': ''
            }), 500

    @face_bp.route('/<username>', methods=['POST'])
    def insert(username):
        try:
            v = verify(request.args, admin=True)
            if v:
                return v

            if 'front' not in request.files:
                return res_cors({
                    'code': 400,
                    'message': 'Missing "front"',
                    'data': ''
                }), 400
            if 'left' not in request.files:
                return res_cors({
                    'code': 400,
                    'message': 'Missing "left"',
                    'data': ''
                }), 400
            if 'right' not in request.files:
                return res_cors({
                    'code': 400,
                    'message': 'Missing "right"',
                    'data': ''
                }), 400

            if not moodle_user(username):
                return res_cors({
                    'code': 404,
                    'message': 'Username not found',
                    'data': ''
                }), 404

            front = load_img(request.files['front'])
            left = load_img(request.files['left'])
            right = load_img(request.files['right'])
            code, result = face_api.create_user(username, front, left, right)

            if code == 201:
                front.save(f'data/{username}_front.jpg')
                left.save(f'data/{username}_left.jpg')
                right.save(f'data/{username}_right.jpg')

            return res_cors({
                'code': code,
                'message': result,
                'data': ''
            }), code
        except Exception as ex:
            print(f'\n***FACE Insert_users error: {ex}***\n')
            return res_cors({
                'code': 500,
                'message': str(ex),
                'data': ''
            }), 500

    @face_bp.route('/<username>', methods=['PUT'])
    def update(username):
        try:
            v = verify(request.args, admin=True)
            if v:
                return v

            if 'front' not in request.files:
                return res_cors({
                    'code': 400,
                    'message': 'Missing "front"',
                    'data': ''
                }), 400
            if 'left' not in request.files:
                return res_cors({
                    'code': 400,
                    'message': 'Missing "left"',
                    'data': ''
                }), 400
            if 'right' not in request.files:
                return res_cors({
                    'code': 400,
                    'message': 'Missing "right"',
                    'data': ''
                }), 400

            front = load_img(request.files['front'])
            left = load_img(request.files['left'])
            right = load_img(request.files['right'])
            code, result = face_api.update_user(username, front, left, right)

            if code == 200:
                front.save(f'data/{username}_front.jpg')
                left.save(f'data/{username}_left.jpg')
                right.save(f'data/{username}_right.jpg')

            return res_cors({
                'code': code,
                'message': result,
                'data': ''
            }), code
        except Exception as ex:
            print(f'\n***FACE Update_users error: {ex}***\n')
            return res_cors({
                'code': 500,
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
                if os.path.isfile(f'data/{username}_front.jpg'):
                    os.remove(f'data/{username}_front.jpg')
                    if os.path.isfile(f'data/{username}_left.jpg'):
                        os.remove(f'data/{username}_left.jpg')
                        if os.path.isfile(f'data/{username}_right.jpg'):
                            os.remove(f'data/{username}_right.jpg')

            return res_cors({
                'code': code,
                'message': result,
                'data': ''
            }), code
        except Exception as ex:
            print(f'\n***FACE Remove_users error: {ex}***\n')
            return res_cors({
                'code': 500,
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
                    'code': 400,
                    'message': 'Missing "image"',
                    'data': ''
                }), 400

            users = []
            for image in request.form.getlist('image'):
                img = load_img_base64(image)

                code, username = face_api.verify(img)
                if code != 200:
                    continue

                if not moodle_checkin(session_id, username, 1):
                    continue

                user = moodle_user(username)
                if user:
                    users.append({
                        user
                    })

            return res_cors({
                'code': 200,
                'message': 'Successful',
                'data': users
            }), 200
        except Exception as ex:
            print(f'\n***FACE Check_user error: {ex}***\n')
            return res_cors({
                'code': 500,
                'message': str(ex),
                'data': ''
            }), 500

    return face_bp
