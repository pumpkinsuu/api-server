from flask import request, Blueprint, jsonify
from face_service.api import FaceAPI


def create_api_bp(face_api: FaceAPI):
    api_bp = Blueprint('api_bp', __name__)

    @api_bp.route('/<collection>/users/<user_id>', methods=['GET'])
    def get_user(collection, user_id):
        try:
            code, result = face_api.get_user(collection, user_id)

            return jsonify({'result': result}), code
        except Exception as ex:
            print(ex)
            return jsonify({'error': str(ex)}), 500

    @api_bp.route('/<collection>/users', methods=['GET'])
    def get_users(collection):
        try:
            code, result = face_api.get_users(collection)

            return jsonify({'result': result}), code
        except Exception as ex:
            print(ex)
            return jsonify({'error': str(ex)}), 500

    @api_bp.route('/<collection>/users/<user_id>', methods=['POST', 'PUT'])
    def update_user(collection, user_id):
        try:
            if 'front' not in request.form:
                return jsonify({'error': 'missing front'}), 400
            if 'left' not in request.form:
                return jsonify({'error': 'missing front'}), 400
            if 'right' not in request.form:
                return jsonify({'error': 'missing front'}), 400

            if request.method == 'POST':
                code, result = face_api.create_user(
                    collection,
                    user_id,
                    front=request.form['front'],
                    left=request.form['left'],
                    right=request.form['right']
                )
            else:
                code, result = face_api.update_user(
                    collection,
                    user_id,
                    front=request.form['front'],
                    left=request.form['left'],
                    right=request.form['right']
                )

            return jsonify({'result': result}), code
        except Exception as ex:
            print(ex)
            return jsonify({'error': str(ex)}), 500

    @api_bp.route('/<collection>/users/<user_id>', methods=['DELETE'])
    def remove_user(collection, user_id):
        try:
            code, result = face_api.remove_user(collection, user_id)

            return jsonify({'result': result}), code
        except Exception as ex:
            print(ex)
            return jsonify({'error': str(ex)}), 500

    @api_bp.route('/<collection>/verify', methods=['POST'])
    def verify(collection):
        try:
            result = []
            for image in request.form.getlist('images'):
                code, username = face_api.verify(collection, image)
                if code != 500:
                    result.append(username)

            return jsonify({'result': result}), 200
        except Exception as ex:
            print(ex)
            return jsonify({'error': str(ex)}), 500

    @api_bp.route('/<collection>', methods=['GET'])
    def count_collection(collection):
        try:
            code, result = face_api.count_collection(collection)

            return jsonify({'result': result}), code
        except Exception as ex:
            print(ex)
            return jsonify({'error': str(ex)}), 500

    @api_bp.route('/<collection>', methods=['PUT'])
    def rename_collection(collection):
        try:
            if 'name' not in request.form:
                return jsonify({'error': 'missing collection'}), 400

            code, result = face_api.rename_collection(collection, request.form['name'])

            return jsonify({'result': result}), code
        except Exception as ex:
            print(ex)
            return jsonify({'error': str(ex)}), 500

    @api_bp.route('/<collection>', methods=['DELETE'])
    def drop_collection(collection):
        try:
            code, result = face_api.drop_collection(collection)
            return jsonify({'result': result}), code
        except Exception as ex:
            print(ex)
            return jsonify({'error': str(ex)}), 500

    return api_bp
