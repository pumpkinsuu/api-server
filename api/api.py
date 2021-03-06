from flask import Blueprint, request
from moodle_service import *


api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/login', methods=['POST'])
def login():
    try:
        if 'username' not in request.json:
            return jsonify({
                'status': 400,
                'message': 'missing "username"',
                'data': ''
            }), 200
        if 'password' not in request.json:
            return jsonify({
                'status': 400,
                'message': 'missing "password"',
                'data': ''
            }), 200

        result = moodle_login(request.json['username'], request.json['password'])
        if result:
            user = moodle_user(request.json['username'])
            user['token'] = result['token']

            return jsonify({
                'status': 200,
                'message': 'success',
                'data': user
            }), 200

        return jsonify({
            'status': 401,
            'message': 'wrong username or password',
            'data': ''
        }), 200
    except Exception as ex:
        print(f'\n***API Login error: {ex}***\n')
        return jsonify({
            'status': 500,
            'message': str(ex),
            'data': ''
        }), 500


@api_bp.route('/get-student-reports ', methods=['GET'])
def get_student_log():
    try:
        v = verify(request.args)
        if v:
            return v

        if 'studentid' not in request.args:
            return jsonify({
                'status': 400,
                'message': 'missing "studentid"',
                'data': ''
            }), 200
        if 'courseid' not in request.args:
            return jsonify({
                'status': 400,
                'message': 'missing "courseid"',
                'data': ''
            }), 200

        log = moodle_student_log(request.args['studentid'], request.args['courseid'])
        if log:
            return jsonify({
                'status': 200,
                'message': 'success',
                'data': log
            }), 200

        return jsonify({
            'status': 404,
            'message': 'student\'s log not found',
            'data': ''
        }), 200
    except Exception as ex:
        print(f'\n***API Get_session error: {ex}***\n')
        return jsonify({
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
            return jsonify({
                'status': 200,
                'message': 'success',
                'data': logs
            }), 200

        return jsonify({
            'status': 404,
            'message': 'course not found',
            'data': ''
        }), 200
    except Exception as ex:
        print(f'\n***API Get_log_by_course error: {ex}***\n')
        return jsonify({
            'status': 500,
            'message': str(ex),
            'data': ''
        }), 500


@api_bp.route('/room-schedules', methods=['GET'])
def room_schedule():
    try:
        if 'roomid' not in request.args:
            return jsonify({
                'status': 400,
                'message': 'missing "roomid"',
                'data': ''
            }), 200
        if 'date' not in request.args:
            return jsonify({
                'status': 400,
                'message': 'missing "date"',
                'data': ''
            }), 200

        v = verify(request.args)
        if v:
            return v

        schedule = moodle_room_schedule(request.args['roomid'], request.args['date'])
        if schedule:
            return jsonify({
                'status': 200,
                'message': 'success',
                'data': schedule
            }), 200

        return jsonify({
            'status': 404,
            'message': 'schedule not found',
            'data': ''
        }), 200
    except Exception as ex:
        print(f'\n***API Get_schedule error: {ex}***\n')
        return jsonify({
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
            return jsonify({
                'status': 400,
                'message': 'missing "campus"',
                'data': ''
            }), 200

        log = moodle_room_by_campus(request.args['campus'])
        if log:
            return jsonify({
                'status': 200,
                'message': 'success',
                'data': log
            }), 200

        return jsonify({
            'status': 404,
            'message': 'campus not found',
            'data': ''
        }), 200
    except Exception as ex:
        print(f'\n***API Get_rooms error: {ex}***\n')
        return jsonify({
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

        user = moodle_token(request.args)

        logs = moodle_get_course(request.args, user['userid'])
        if logs:
            return jsonify({
                'status': 200,
                'message': 'success',
                'data': logs
            }), 200

        return jsonify({
            'status': 404,
            'message': 'attendance not found',
            'data': ''
        }), 200
    except Exception as ex:
        print(f'\n***API Get_session error: {ex}***\n')
        return jsonify({
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
            return jsonify({
                'status': 200,
                'message': 'success',
                'data': session
            }), 200

        return jsonify({
            'status': 404,
            'message': 'session not found',
            'data': ''
        }), 200
    except Exception as ex:
        print(f'\n***API Get_session error: {ex}***\n')
        return jsonify({
            'status': 500,
            'message': str(ex),
            'data': ''
        }), 500


@api_bp.route('/update-attendance-log/<room_id>', methods=['POST'])
def manual_check(room_id):
    try:
        v = verify(request.args)
        if v:
            return v

        if 'students' not in request.json:
            return jsonify({
                'status': 400,
                'message': 'missing "students"',
                'data': ''
            }), 200

        for student in request.json['students']:
            if not moodle_checkin(room_id, student['id'], student['status']):
                return jsonify({
                    'status': 400,
                    'message': 'failed to checkin',
                    'data': ''
                }), 200

        return jsonify({
            'status': 200,
            'message': 'success',
            'data': ''
        }), 200
    except Exception as ex:
        print(f'\n***API Manual_check error: {ex}***\n')
        return jsonify({
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
            return jsonify({
                'status': 200,
                'message': 'success',
                'data': student
            }), 200

        return jsonify({
            'status': 404,
            'message': 'username not found',
            'data': ''
        }), 200
    except Exception as ex:
        print(f'\n***API Get_student error: {ex}***\n')
        return jsonify({
            'status': 500,
            'message': str(ex),
            'data': ''
        }), 500


@api_bp.route('/campus', methods=['GET'])
def get_campus():
    try:
        v = verify(request.args)
        if v:
            return v

        return jsonify({
            'status': 200,
            'message': 'success',
            'data': [
                {
                    'id': 'NVC',
                    'name': 'Nguyễn Văn Cừ'
                },
                {
                    'id': 'LT',
                    'name': 'Linh Trung'
                }
            ]
        }), 200
    except Exception as ex:
        print(f'\n***API Get_campus error: {ex}***\n')
        return jsonify({
            'status': 500,
            'message': str(ex),
            'data': ''
        }), 500

