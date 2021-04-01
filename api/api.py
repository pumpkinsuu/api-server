from flask import Blueprint, request
from moodle_service import *


api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/login', methods=['POST'])
def login():
    try:
        if 'username' not in request.form:
            return res_cors({
                'code': 400,
                'message': 'Missing "username"',
                'data': ''
            }), 400
        if 'password' not in request.form:
            return res_cors({
                'code': 400,
                'message': 'Missing "password"',
                'data': ''
            }), 400

        result = moodle_login(request.form['username'], request.form['password'])
        if result:
            user = moodle_user(request.form['username'])
            user['token'] = result['token']

            return res_cors({
                'code': 200,
                'message': 'Successful',
                'data': user
            }), 200

        return res_cors({
            'code': 401,
            'message': 'Wrong username or password',
            'data': ''
        }), 401
    except Exception as ex:
        print(f'\n***API Login error: {ex}***\n')
        return res_cors({
            'code': 500,
            'message': str(ex),
            'data': ''
        }), 500


@api_bp.route('/room-schedules', methods=['GET'])
def room_schedule():
    try:
        if 'roomid' not in request.args:
            return res_cors({
                'code': 400,
                'message': 'Missing "roomid"',
                'data': ''
            }), 400
        if 'date' not in request.args:
            return res_cors({
                'code': 400,
                'message': 'Missing "date"',
                'data': ''
            }), 400

        v = verify(request.args)
        if v:
            return v

        schedule = moodle_room_schedule(request.args['roomid'], request.args['date'])
        if schedule:
            return res_cors({
                'code': 200,
                'message': 'Successful',
                'data': schedule
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
            'message': str(ex),
            'data': ''
        }), 500


@api_bp.route('/session/<session_id>', methods=['GET'])
def get_session(session_id):
    try:
        v = verify(request.args)
        if v:
            return v

        session = moodle_session(session_id)
        if session:
            return res_cors({
                'code': 200,
                'message': 'Successful',
                'data': session
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
            'message': str(ex),
            'data': ''
        }), 500


@api_bp.route('/log', methods=['GET'])
def get_log():
    try:
        v = verify(request.args)
        if v:
            return v

        if 'studentid' not in request.args:
            return res_cors({
                'code': 400,
                'message': 'Missing "studentid"',
                'data': ''
            }), 400
        if 'sessionid' not in request.args:
            return res_cors({
                'code': 400,
                'message': 'Missing "sessionid"',
                'data': ''
            }), 400

        log = moodle_log(request.args['studentid'], request.args['sessionid'])
        if log:
            return res_cors({
                'code': 200,
                'message': 'Successful',
                'data': log
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
            'message': str(ex),
            'data': ''
        }), 500


@api_bp.route('/teacher-schedules/<attendance_id>', methods=['GET'])
def get_logs(attendance_id):
    try:
        v = verify(request.args)
        if v:
            return v

        logs = moodle_logs(attendance_id)
        if logs:
            return res_cors({
                'code': 200,
                'message': 'Successful',
                'data': logs
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
            'message': str(ex),
            'data': ''
        }), 500


@api_bp.route('/students/<username>', methods=['GET'])
def get_student(username):
    try:
        v = verify(request.args)
        if v:
            return v

        student = moodle_user(username)
        if student:
            return res_cors({
                'code': 200,
                'message': 'Successful',
                'data': student
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
            'message': str(ex),
            'data': ''
        }), 500


@api_bp.route('/update-attendance-log/<session_id>', methods=['POST'])
def manual_check(session_id):
    try:
        v = verify(request.args)
        if v:
            return v

        if 'students' not in request.json:
            return res_cors({
                'code': 400,
                'message': 'Missing "students"',
                'data': ''
            }), 400

        for student in request.json['students']:
            moodle_checkin(session_id, student['id'], student['status'])

        return res_cors({
            'code': 200,
            'message': 'Successful',
            'data': ''
        }), 200
    except Exception as ex:
        print(f'\n***API Manual_check error: {ex}***\n')
        return res_cors({
            'code': 500,
            'message': str(ex),
            'data': ''
        }), 500

