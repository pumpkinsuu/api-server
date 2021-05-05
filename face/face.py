from flask import Blueprint, request

from face_service.api import FaceAPI
from photo_service.api import PhotoAPI
from moodle_service import *


def create_face_bp(face_api: FaceAPI, photo_api: PhotoAPI):
    face_bp = Blueprint('face_bp', __name__)

    @face_bp.route('/<collection>', methods=['GET'])
    def get_users(collection):
        try:
            v = verify(request.args)
            if v:
                return v

            code, result = face_api.get_users(collection)

            if code == 200:
                return jsonify({
                    'status': code,
                    'message': 'success',
                    'data': result
                }), code

            return jsonify({
                'status': code,
                'message': result,
                'data': ''
            }), code
        except Exception as ex:
            print(f'\n***FACE Get_users error: {ex}***\n')
            return jsonify({
                'status': 500,
                'message': str(ex),
                'data': ''
            }), 500

    @face_bp.route('/<collection>', methods=['POST'])
    def rename_collection(collection):
        try:
            v = verify(request.args)
            if v:
                return v

            if 'name' not in request.form:
                return jsonify({
                    'status': 400,
                    'message': 'missing "name"',
                    'data': ''
                }), 400
            code, result = face_api.rename_collection(
                collection,
                request.form['name']
            )
            if code == 200:
                return jsonify({
                    'status': code,
                    'message': 'success',
                    'data': result
                }), code
            return jsonify({
                'status': code,
                'message': result,
                'data': ''
            }), code
        except Exception as ex:
            print(f'\n***FACE Rename_collection error: {ex}***\n')
            return jsonify({
                'status': 500,
                'message': str(ex),
                'data': ''
            }), 500

    @face_bp.route('/<collection>', methods=['DELETE'])
    def drop_collection(collection):
        try:
            v = verify(request.args)
            if v:
                return v

            code, result = face_api.drop_collection(collection)
            if code == 200:
                return jsonify({
                    'status': code,
                    'message': 'success',
                    'data': result
                }), code
            return jsonify({
                'status': code,
                'message': result,
                'data': ''
            }), code
        except Exception as ex:
            print(f'\n***FACE Drop_collection error: {ex}***\n')
            return jsonify({
                'status': 500,
                'message': str(ex),
                'data': ''
            }), 500

    @face_bp.route('/<collection>/<username>', methods=['GET'])
    def get_user(collection, username):
        try:
            v = verify(request.args)
            if v:
                return v

            code, result = face_api.get_user(collection, username)

            if code == 200:
                code, result = photo_api.get_user(collection, username)
                data = {
                    'left': result['left'],
                    'right': result['right'],
                    'front': result['front']
                }

                return jsonify({
                    'status': 200,
                    'message': 'success',
                    'data': data
                }), 200

            return jsonify({
                'status': 404,
                'message': result,
                'data': ''
            }), 404
        except Exception as ex:
            print(f'\n***FACE Get_user error: {ex}***\n')
            return jsonify({
                'status': 500,
                'message': str(ex),
                'data': ''
            }), 500

    @face_bp.route('/<collection>/<username>', methods=['POST', 'PUT'])
    def update_user(collection, username):
        try:
            v = verify(request.args, admin=True)
            if v:
                return v

            if 'front' not in request.form:
                return jsonify({
                    'status': 400,
                    'message': 'missing "front"',
                    'data': ''
                }), 400
            if 'left' not in request.form:
                return jsonify({
                    'status': 400,
                    'message': 'missing "left"',
                    'data': ''
                }), 400
            if 'right' not in request.form:
                return jsonify({
                    'status': 400,
                    'message': 'missing "right"',
                    'data': ''
                }), 400

            if not moodle_user(username):
                return jsonify({
                    'status': 404,
                    'message': 'username not found',
                    'data': ''
                }), 404

            code, result = face_api.get_user(collection, username)

            if code != 200:
                code, result = face_api.create_user(
                    collection,
                    username,
                    front=request.form['front'],
                    left=request.form['left'],
                    right=request.form['right']
                )
                if code == 201:
                    code, result = photo_api.create_user(
                        collection,
                        username,
                        front=request.form['front'],
                        left=request.form['left'],
                        right=request.form['right']
                    )
                    if code != 201:
                        face_api.remove_user(collection, username)

            else:
                code, result = face_api.update_user(
                    collection,
                    username,
                    front=request.form['front'],
                    left=request.form['left'],
                    right=request.form['right']
                )
                if code == 200:
                    code, result = photo_api.update_user(
                        collection,
                        username,
                        front=request.form['front'],
                        left=request.form['left'],
                        right=request.form['right']
                    )

            return jsonify({
                'status': code,
                'message': result,
                'data': ''
            }), code
        except Exception as ex:
            if not face_api.get_user(collection, username) \
                    or not photo_api.get_user(collection, username):
                face_api.remove_user(collection, username)
                photo_api.remove_user(collection, username)

            print(f'\n***FACE Insert_users error: {ex}***\n')
            return jsonify({
                'status': 500,
                'message': str(ex),
                'data': ''
            }), 500

    @face_bp.route('/<collection>/<username>', methods=['DELETE'])
    def remove(collection, username):
        try:
            v = verify(request.args, admin=True)
            if v:
                return v

            code, result = face_api.remove_user(collection, username)

            if code == 200:
                code, result = photo_api.remove_user(collection, username)

            return jsonify({
                'status': code,
                'message': result,
                'data': ''
            }), code
        except Exception as ex:
            print(f'\n***FACE Remove_users error: {ex}***\n')
            return jsonify({
                'status': 500,
                'message': str(ex),
                'data': ''
            }), 500

    @face_bp.route('/checkin/<room_id>', methods=['POST'])
    def check(room_id):
        try:
            v = verify(request.args)
            if v:
                return v

            if 'images' not in request.json:
                return jsonify({
                    'status': 400,
                    'message': 'missing "images"',
                    'data': ''
                }), 400

            if 'collection' not in request.json:
                return jsonify({
                    'status': 400,
                    'message': 'missing "collection"',
                    'data': ''
                }), 400

            users = []
            for image in request.json.getlist('images'):
                code, username = face_api.verify(
                    request.json['collection'],
                    image
                )

                if code != 200:
                    users.append({'status': 0})
                    continue

                user = moodle_user(username)
                if user:
                    if moodle_checkin(room_id, username, 1):
                        user['status'] = 1
                    else:
                        user['status'] = 2

                    code, result = photo_api.get_user(
                        request.json['collection'],
                        username
                    )
                    if code == 200:
                        user['avatar'] = result['front']

                    users.append(user)

            return jsonify({
                'status': 200,
                'message': 'success',
                'data': users
            }), 200
        except Exception as ex:
            print(f'\n***FACE Check_user error: {ex}***\n')
            return jsonify({
                'status': 500,
                'message': str(ex),
                'data': ''
            }), 500

    @face_bp.route('/verify', methods=['POST'])
    def face_verify():
        try:
            code, result = face_api.verify(
                request.form['collection'],
                request.form['image']
            )
            return jsonify({
                'status': code,
                'message': 'success',
                'data': result
            }), code
        except Exception as ex:
            print(f'\n***FACE Check_user error: {ex}***\n')
            return jsonify({
                'status': 500,
                'message': str(ex),
                'data': ''
            }), 500

    @face_bp.route('/feedback', methods=['POST'])
    def face_feedback():
        try:
            v = verify(request.args)
            if v:
                return v

            if 'image' not in request.form:
                return jsonify({
                    'status': 400,
                    'message': 'missing "image"',
                    'data': ''
                }), 400

            if 'collection' not in request.form:
                return jsonify({
                    'status': 400,
                    'message': 'missing "collection"',
                    'data': ''
                }), 400

            if 'roomid' not in request.form:
                return jsonify({
                    'status': 400,
                    'message': 'missing "roomid"',
                    'data': ''
                }), 400

            if 'usertaken' not in request.form:
                return jsonify({
                    'status': 400,
                    'message': 'missing "usertaken"',
                    'data': ''
                }), 400

            if 'userbetaken' not in request.form:
                return jsonify({
                    'status': 400,
                    'message': 'missing "userbetaken"',
                    'data': ''
                }), 400

            description = 'Mistaken in face recognition'
            if 'description' in request.form:
                description = request.form['description']

            code, result = face_api.get_user(
                request.form['collection'],
                request.form['usertaken'])

            if code == 200:
                _, _ = photo_api.create_feedback(
                    request.form['collection'],
                    request.form['usertaken'],
                    request.form['roomid'],
                    request.form['image']
                )

                url = f'{request.form["collection"]}' \
                      f'/{request.form["roomid"]}' \
                      f'/{request.form["usertaken"]}'

                if moodle_create_feedback(
                        request.form['roomid'],
                        request.form['usertaken'],
                        request.form['userbetaken'],
                        description,
                        url
                ):
                    return jsonify({
                        'status': 200,
                        'message': 'success',
                        'data': ''
                    }), 200
                else:
                    return jsonify({
                        'status': 500,
                        'message': 'webservices error',
                        'data': ''
                    }), 500

            return jsonify({
                'status': 404,
                'message': 'usertaken not exist',
                'data': ''
            }), 404

        except Exception as ex:
            print(f'\n***FACE Create_feedback error: {ex}***\n')
            return jsonify({
                'status': 500,
                'message': str(ex),
                'data': ''
            }), 500

    return face_bp
