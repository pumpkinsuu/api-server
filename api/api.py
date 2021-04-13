from flask import Blueprint, request
from moodle_service import *


api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/login', methods=['POST'])
def login():
    try:
        if 'username' not in request.json:
            return res_cors({
                'status': 400,
                'message': 'missing "username"',
                'data': ''
            }), 400
        if 'password' not in request.json:
            return res_cors({
                'status': 400,
                'message': 'missing "password"',
                'data': ''
            }), 400

        result = moodle_login(request.json['username'], request.json['password'])
        if result:
            user = moodle_user(request.json['username'])
            user['token'] = result['token']

            return res_cors({
                'status': 200,
                'message': 'success',
                'data': user
            }), 200

        return res_cors({
            'status': 401,
            'message': 'wrong username or password',
            'data': ''
        }), 401
    except Exception as ex:
        print(f'\n***API Login error: {ex}***\n')
        return res_cors({
            'status': 500,
            'message': str(ex),
            'data': ''
        }), 500


@api_bp.route('/get-reports/<course_id>', methods=['GET'])
def get_log_by_course(course_id):
    try:
        v = verify(request.args)
        if v:
            return v

        logs = moodle_log_by_course(course_id)
        if logs:
            return res_cors({
                'status': 200,
                'message': 'success',
                'data': logs
            }), 200

        return res_cors({
            'status': 404,
            'message': 'course not found',
            'data': ''
        }), 404
    except Exception as ex:
        print(f'\n***API Get_log_by_course error: {ex}***\n')
        return res_cors({
            'status': 500,
            'message': str(ex),
            'data': ''
        }), 500


@api_bp.route('/room-schedules', methods=['GET'])
def room_schedule():
    try:
        if 'roomid' not in request.args:
            return res_cors({
                'status': 400,
                'message': 'missing "roomid"',
                'data': ''
            }), 400
        if 'date' not in request.args:
            return res_cors({
                'status': 400,
                'message': 'missing "date"',
                'data': ''
            }), 400

        v = verify(request.args)
        if v:
            return v

        schedule = moodle_room_schedule(request.args['roomid'], request.args['date'])
        if schedule:
            return res_cors({
                'status': 200,
                'message': 'success',
                'data': schedule
            }), 200

        return res_cors({
            'status': 404,
            'message': 'schedule not found',
            'data': ''
        }), 404
    except Exception as ex:
        print(f'\n***API Get_schedule error: {ex}***\n')
        return res_cors({
            'status': 500,
            'message': str(ex),
            'data': ''
        }), 500


@api_bp.route('/rooms', methods=['GET'])
def get_rooms():
    try:
        v = verify(request.args)
        if v:
            return v

        if 'campus' not in request.args:
            return res_cors({
                'status': 400,
                'message': 'missing "campus"',
                'data': ''
            }), 400

        log = moodle_room_by_campus(request.args['campus'])
        if log:
            return res_cors({
                'status': 200,
                'message': 'success',
                'data': log
            }), 200

        return res_cors({
            'status': 404,
            'message': 'campus not found',
            'data': ''
        }), 404
    except Exception as ex:
        print(f'\n***API Get_rooms error: {ex}***\n')
        return res_cors({
            'status': 500,
            'message': str(ex),
            'data': ''
        }), 500


@api_bp.route('/teacher-schedules', methods=['GET'])
def get_log():
    try:
        v = verify(request.args)
        if v:
            return v

        user = moodle_token(request.args['token'])

        logs = moodle_get_course(request.args['token'], user['userid'])
        if logs:
            return res_cors({
                'status': 200,
                'message': 'success',
                'data': logs
            }), 200

        return res_cors({
            'status': 404,
            'message': 'attendance not found',
            'data': ''
        }), 404
    except Exception as ex:
        print(f'\n***API Get_session error: {ex}***\n')
        return res_cors({
            'status': 500,
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
                'status': 200,
                'message': 'success',
                'data': session
            }), 200

        return res_cors({
            'status': 404,
            'message': 'session not found',
            'data': ''
        }), 404
    except Exception as ex:
        print(f'\n***API Get_session error: {ex}***\n')
        return res_cors({
            'status': 500,
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
                'status': 400,
                'message': 'missing "students"',
                'data': ''
            }), 400

        for student in request.json['students']:
            moodle_checkin(session_id, student['id'], student['status'])

        return res_cors({
            'status': 200,
            'message': 'success',
            'data': ''
        }), 200
    except Exception as ex:
        print(f'\n***API Manual_check error: {ex}***\n')
        return res_cors({
            'status': 500,
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
                'status': 200,
                'message': 'success',
                'data': student
            }), 200

        return res_cors({
            'status': 404,
            'message': 'username not found',
            'data': ''
        }), 404
    except Exception as ex:
        print(f'\n***API Get_student error: {ex}***\n')
        return res_cors({
            'status': 500,
            'message': str(ex),
            'data': ''
        }), 500


@api_bp.route('/log', methods=['GET'])
def get_student_log():
    try:
        v = verify(request.args)
        if v:
            return v

        if 'studentid' not in request.args:
            return res_cors({
                'status': 400,
                'message': 'missing "studentid"',
                'data': ''
            }), 400
        if 'sessionid' not in request.args:
            return res_cors({
                'status': 400,
                'message': 'missing "sessionid"',
                'data': ''
            }), 400

        log = moodle_student_log(request.args['studentid'], request.args['sessionid'])
        if log:
            return res_cors({
                'status': 200,
                'message': 'success',
                'data': log
            }), 200

        return res_cors({
            'status': 404,
            'message': 'student\'s log not found',
            'data': ''
        }), 404
    except Exception as ex:
        print(f'\n***API Get_session error: {ex}***\n')
        return res_cors({
            'status': 500,
            'message': str(ex),
            'data': ''
        }), 500
