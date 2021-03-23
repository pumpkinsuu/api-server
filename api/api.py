from flask import Blueprint, request
from config import *


api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/login', methods=['POST'])
def login():
    try:
        if 'username' not in request.form:
            return res_cors({
                'code': 400,
                'message': 'Bad request',
                'data': ''
            }), 400
        if 'password' not in request.form:
            return res_cors({
                'code': 400,
                'message': 'Bad request',
                'data': ''
            }), 400

        """url = f'{HOST}/login/token.php' \
              f'?moodlewsrestformat=json' \
              f'&service=moodle_mobile_app' \
              f'&username={request.form["username"]}' \
              f'&password={request.form["password"]}'
        r = req.post(url)

        if r.status_code == 200:
            return res_cors({
                'code': 200,
                'message': 'Successful',
                'data': r.json()
            }), 200"""

        if request.form["username"] == 'admin' and request.form["password"] == 'admin':
            return res_cors({
                'code': 200,
                'message': 'Successful',
                'data': {
                    'id': 1,
                    'token': 'adsa212',
                    'role': 1,
                    'avatar': 'adsads'
                }
            }), 200

        return res_cors({'error': 'Wrong username or password'}), 401
    except Exception as ex:
        print(f'\n***API Login error: {ex}***\n')
        return res_cors({
            'code': 500,
            'message': 'Internal Server Error',
            'data': ''
        }), 500


@api_bp.route('/room-schedules', methods=['GET'])
def room_schedule():
    try:
        if 'id' not in request.args:
            return res_cors({
                'code': 400,
                'message': 'Bad request',
                'data': ''
            }), 400
        if 'date' not in request.args:
            return res_cors({
                'code': 400,
                'message': 'Bad request',
                'data': ''
            }), 400

        v = verify(request.args)
        if v:
            return v

        url = f'{HOST}/webservice/rest/server.php' \
              f'?moodlewsrestformat=json' \
              f'&service=moodle_mobile_app' \
              f'&wstoken={WSTOKEN}' \
              f'&wsfunction={ROOM_SCHEDULE}'
        r = req.post(url)

        if r.status_code == 200:
            return res_cors({
                'code': 200,
                'message': 'Successful',
                'data': r.json()
            }), 200

        return res_cors({
            'code': 404,
            'message': 'Not found',
            'data': ''
        }), 404
    except Exception as ex:
        print(f'\n***API Get_schedule error: {ex}***\n')
        return res_cors({
            'code': 500,
            'message': 'Internal Server Error',
            'data': ''
        }), 500


@api_bp.route('/session/<int:ID>', methods=['GET'])
def session(ID):
    try:
        v = verify(request.args)
        if v:
            return v

        url = f'{HOST}/webservice/rest/server.php' \
              f'?moodlewsrestformat=json' \
              f'&service=moodle_mobile_app' \
              f'&wstoken={WSTOKEN}' \
              f'&wsfunction={SESSION}' \
              f'&id={ID}'
        r = req.post(url)

        if r.status_code == 200:
            return res_cors({
                'code': 200,
                'message': 'Successful',
                'data': r.json()
            }), 200

        return res_cors({
            'code': 404,
            'message': 'Not found',
            'data': ''
        }), 404
    except Exception as ex:
        print(f'\n***API Get_session error: {ex}***\n')
        return res_cors({
            'code': 500,
            'message': 'Internal Server Error',
            'data': ''
        }), 500


@api_bp.route('/students/<int:ID>', methods=['GET'])
def student(ID):
    try:
        v = verify(request.args)
        if v:
            return v

        url = f'{HOST}/webservice/rest/server.php' \
              f'?moodlewsrestformat=json' \
              f'&service=moodle_mobile_app' \
              f'&wstoken={WSTOKEN}' \
              f'&wsfunction={GET_USER}' \
              f'&id={ID}'
        r = req.post(url)

        if r.status_code == 200:
            return res_cors({
                'code': 200,
                'message': 'Successful',
                'data': r.json()
            }), 200

        return res_cors({
            'code': 404,
            'message': 'Not found',
            'data': ''
        }), 404
    except Exception as ex:
        print(f'\n***API Get_student error: {ex}***\n')
        return res_cors({
            'code': 500,
            'message': 'Internal Server Error',
            'data': ''
        }), 500


@api_bp.route('/update-attendance-log/<int:ID>', methods=['POST'])
def manual_check(ID):
    try:
        v = verify(request.args)
        if v:
            return v

        if 'students' not in request.json:
            return res_cors({
                'code': 400,
                'message': 'Bad request',
                'data': ''
            }), 400

        for student in request.json['students']:
            url = f'{HOST}/webservice/rest/server.php' \
                  f'?moodlewsrestformat=json' \
                  f'&service=moodle_mobile_app' \
                  f'&wstoken={WSTOKEN}' \
                  f'&wsfunction={POST_REPORT}' \
                  f'&id={ID}' \
                  f'&studentID={student["id"]}' \
                  f'&status={student["status"]}'
            r = req.post(url)

            if r.status_code != 200:
                return res_cors({
                    'code': 404,
                    'message': 'Not found',
                    'data': f'{student["id"]}'
                }), 404

        return res_cors({
            'code': 200,
            'message': 'Successful',
            'data': ''
        }), 200
    except Exception as ex:
        print(f'\n***API Manual_check error: {ex}***\n')
        return res_cors({
            'code': 500,
            'message': 'Internal Server Error',
            'data': ''
        }), 500

