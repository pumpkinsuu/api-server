from face_model.dlib_model import Model
from database import DataBase
from flask import Blueprint, request
import os
from config import *


def create_face_bp(app):
    db_name = 'face_db'
    db_pass = 'AdminPass123'
    cluster = 'cluster0.qe6sa.mongodb.net'
    db = DataBase(app, db_name, db_pass, cluster)

    model = Model()
    face_bp = Blueprint('face_bp', __name__)

    @face_bp.route('/', methods=['GET'])
    def get_users():
        try:
            v = verify(request.args)
            if v:
                return v

            ids, _ = db.get_users()

            if len(ids) != 0:
                return res_cors({
                    'code': 200,
                    'message': 'Successful',
                    'data': ids
                }), 200

            return res_cors({
                'code': 404,
                'message': 'Not found',
                'data': ''
            }), 404
        except Exception as ex:
            print(f'\n***FACE Get_users error: {ex}***\n')
            return res_cors({
                'code': 500,
                'message': 'Internal Server Error',
                'data': ''
            }), 500

    @face_bp.route('/<int:ID>', methods=['GET'])
    def get_user(ID):
        try:
            v = verify(request.args)
            if v:
                return v

            user = db.get_user(ID)

            if user:
                return res_cors({
                    'code': 200,
                    'message': 'Successful',
                    'data': {
                        'front': encode_img(f'data/{user["id"]}_front.jpg'),
                        'left': encode_img(f'data/{user["id"]}_left.jpg'),
                        'right': encode_img(f'data/{user["id"]}_right.jpg')
                    }
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
                'message': 'Internal Server Error',
                'data': ''
            }), 500

    @face_bp.route('/<int:ID>', methods=['POST'])
    def insert(ID):
        try:
            v = verify(request.args)
            if v:
                return v

            if 'front' not in request.files:
                return res_cors({
                    'code': 400,
                    'message': 'Bad request',
                    'data': ''
                }), 400
            if 'left' not in request.files:
                return res_cors({
                    'code': 400,
                    'message': 'Bad request',
                    'data': ''
                }), 400
            if 'right' not in request.files:
                return res_cors({
                    'code': 400,
                    'message': 'Bad request',
                    'data': ''
                }), 400

            url = f'{HOST}/webservice/rest/server.php' \
                  f'?moodlewsrestformat=json' \
                  f'&service=moodle_mobile_app' \
                  f'&wstoken={WSTOKEN}' \
                  f'&wsfunction={LIST_USER}'
            r = req.post(url)

            users = r.json()
            if ID not in users:
                return res_cors({
                    'code': 404,
                    'message': 'Not found',
                    'data': ''
                }), 404

            db_ids, db_embeds = db.get_users()
            # Check user exist
            if ID in db_ids:
                return res_cors({
                    'code': 409,
                    'message': 'ID registered',
                    'data': ''
                }), 409

            embeds = []

            front = load_img(request.files['front'])
            if front.shape != model.size:
                return res_cors({
                    'code': 400,
                    'message': f'Image\'s size: {model.size} not {front.shape}',
                    'data': ''
                }), 400
            embeds.append(model.get_embed(front))

            left = load_img(request.files['left'])
            if left.shape != model.size:
                return res_cors({
                    'code': 400,
                    'message': f'Image\'s size: {model.size} not {left.shape}',
                    'data': ''
                }), 400
            embeds.append(model.get_embed(left))

            right = load_img(request.files['right'])
            if right.shape != model.size:
                return res_cors({
                    'code': 400,
                    'message': f'Image\'s size: {model.size} not {right.shape}',
                    'data': ''
                }), 400
            embeds.append(model.get_embed(right))

            # Check same person face
            if distance(embeds[0], embeds[1]) > model.tol or distance(embeds[0], embeds[2]) > model.tol:
                return res_cors({
                    'code': 400,
                    'message': 'Different faces',
                    'data': ''
                }), 400

            # Get mean embeds
            user = {
                'id': ID,
                'embed': mean(embeds)
            }

            # Check embeds exist
            if db_embeds:
                db_embeds = np.array(db_embeds)
                idx, dist = find_min(user['embed'], db_embeds)
                if dist < model.tol:
                    return res_cors({
                        'code': 409,
                        'message': 'Face registered',
                        'data': ''
                    }), 409

            # Insert user to database
            user['embed'] = user['embed'].tolist()
            if db.insert(user):
                save_img(f'data/{user["id"]}_front.jpg', front)
                save_img(f'data/{user["id"]}_left.jpg', left)
                save_img(f'data/{user["id"]}_right.jpg', right)

                return res_cors({
                    'code': 201,
                    'message': 'Successful',
                    'data': ''
                }), 201

            return res_cors({'error': 'Database error'}), 500
        except Exception as ex:
            print(f'\n***FACE Insert_users error: {ex}***\n')
            return res_cors({
                'code': 500,
                'message': 'Internal Server Error',
                'data': ''
            }), 500

    @face_bp.route('/<int:ID>', methods=['PUT'])
    def update(ID):
        try:
            v = verify(request.args)
            if v:
                return v

            if 'front' not in request.files:
                return res_cors({
                    'code': 400,
                    'message': 'Bad request',
                    'data': ''
                }), 400
            if 'left' not in request.files:
                return res_cors({
                    'code': 400,
                    'message': 'Bad request',
                    'data': ''
                }), 400
            if 'right' not in request.files:
                return res_cors({
                    'code': 400,
                    'message': 'Bad request',
                    'data': ''
                }), 400

            db_ids, db_embeds = db.get_users()
            # Check user exist
            if ID not in db_ids:
                return res_cors({
                    'code': 404,
                    'message': 'Not found',
                    'data': ''
                }), 404

            embeds = []

            front = load_img(request.files['front'])
            if front.shape != model.size:
                return res_cors({
                    'code': 400,
                    'message': f'Image\'s size: {model.size} not {front.shape}',
                    'data': ''
                }), 400
            embeds.append(model.get_embed(front))

            left = load_img(request.files['left'])
            if left.shape != model.size:
                return res_cors({
                    'code': 400,
                    'message': f'Image\'s size: {model.size} not {left.shape}',
                    'data': ''
                }), 400
            embeds.append(model.get_embed(left))

            right = load_img(request.files['right'])
            if right.shape != model.size:
                return res_cors({
                    'code': 400,
                    'message': f'Image\'s size: {model.size} not {right.shape}',
                    'data': ''
                }), 400
            embeds.append(model.get_embed(right))

            # Check same person face
            if distance(embeds[0], embeds[1]) > model.tol or distance(embeds[0], embeds[2]) > model.tol:
                return res_cors({
                    'code': 400,
                    'message': 'Different faces',
                    'data': ''
                }), 400

            # Get mean embeds
            user = {
                'id': ID,
                'embed': mean(embeds)
            }

            # Check embeds exist
            if db_embeds:
                db_embeds = np.array(db_embeds)
                idx, dist = find_min(user['embed'], db_embeds)
                if dist < model.tol and db_ids[idx] != user['id']:
                    return res_cors({
                        'code': 409,
                        'message': 'Face registered',
                        'data': ''
                    }), 409

            # Update user to database
            user['embed'] = user['embed'].tolist()
            if db.update(user):
                save_img(f'data/{user["id"]}_front.jpg', front)
                save_img(f'data/{user["id"]}_left.jpg', left)
                save_img(f'data/{user["id"]}_right.jpg', right)

                return res_cors({
                    'code': 200,
                    'message': 'Successful',
                    'data': ''
                }), 200

            return res_cors({
                'code': 500,
                'message': 'Failed',
                'data': ''
            }), 500
        except Exception as ex:
            print(f'\n***FACE Update_users error: {ex}***\n')
            return res_cors({
                'code': 500,
                'message': 'Internal Server Error',
                'data': ''
            }), 500

    @face_bp.route('/<int:ID>', methods=['DELETE'])
    def remove(ID):
        try:
            v = verify(request.args)
            if v:
                return v

            ids, _ = db.get_users()
            if ID not in ids:
                return res_cors({
                    'code': 404,
                    'message': 'Not found',
                    'data': ''
                }), 404

            if db.remove(ID):
                if os.path.isfile(f'data/{ID}_front.jpg'):
                    os.remove(f'data/{ID}_front.jpg')
                    if os.path.isfile(f'data/{ID}_left.jpg'):
                        os.remove(f'data/{ID}_left.jpg')
                        if os.path.isfile(f'data/{ID}_right.jpg'):
                            os.remove(f'data/{ID}_right.jpg')

                return res_cors({
                    'code': 200,
                    'message': 'Successful',
                    'data': ''
                }), 200

            return res_cors({
                'code': 500,
                'message': 'Failed',
                'data': ''
            }), 500
        except Exception as ex:
            print(f'\n***FACE Remove_users error: {ex}***\n')
            return res_cors({
                'code': 500,
                'message': 'Internal Server Error',
                'data': ''
            }), 500

    @face_bp.route('/checkin/<int:ID>', methods=['POST'])
    def check(ID):
        try:
            v = verify(request.args)
            if v:
                return v

            if 'image' not in request.files:
                return res_cors({
                    'code': 400,
                    'message': 'Bad request',
                    'data': ''
                }), 400

            db_ids, db_embeds = db.get_users()
            if not db_ids:
                return res_cors({
                    'code': 500,
                    'message': 'Database empty',
                    'data': ''
                }), 500

            db_embeds = np.array(db_embeds)

            users = []
            for file in request.files.getlist('image'):
                img = load_img(file)

                # Check image size
                if img.shape != model.size:
                    return res_cors({
                        'code': 400,
                        'message': f'Image\'s size: {model.size} not {img.shape}',
                        'data': ''
                    }), 400

                embed = model.get_embed(img)

                idx, dist = find_min(embed, db_embeds)
                if dist <= model.tol:
                    url = f'{HOST}/webservice/rest/server.php' \
                          f'?moodlewsrestformat=json' \
                          f'&service=moodle_mobile_app' \
                          f'&wstoken={WSTOKEN}' \
                          f'&wsfunction={POST_REPORT}' \
                          f'&id={ID}' \
                          f'&studentID={db_ids[idx]}' \
                          f'&status=face'
                    r = req.post(url)

                    if r.status_code != 200:
                        return res_cors({
                            'code': 404,
                            'message': 'Not found',
                            'data': f'{db_ids[idx]}'
                        }), 404

                    url = f'{HOST}/webservice/rest/server.php' \
                          f'?moodlewsrestformat=json' \
                          f'&service=moodle_mobile_app' \
                          f'&wstoken={WSTOKEN}' \
                          f'&wsfunction={GET_USER}' \
                          f'&id={db_ids[idx]}'
                    r = req.post(url)

                    if r.status_code != 200:
                        return res_cors({
                            'code': 404,
                            'message': 'Not found',
                            'data': f'{db_ids[idx]}'
                        }), 404
                    user = r.json()
                    users.append(user)

            return res_cors({
                'code': 200,
                'message': 'Successful',
                'data': users
            }), 200
        except Exception as ex:
            print(f'\n***FACE Check_user error: {ex}***\n')
            return res_cors({
                'code': 500,
                'message': 'Internal Server Error',
                'data': ''
            }), 500

    return face_bp
