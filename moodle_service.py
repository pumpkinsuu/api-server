import requests as req
from flask import jsonify
from utilities import *


HOST = 'http://localhost'
WSTOKEN = '56e75b2279ae442cc8a38aa3eb59f3a8'
USER_INFO = 'local_webservices_get_roles'
TOKEN_INFO = 'core_webservice_get_site_info'
GET_LOG = 'local_webservices_get_logs_by_id'
GET_STUDENT_LOG = 'local_webservices_get_student_logs_by_course_id'
GET_LOG_BY_COURSE = 'local_webservices_get_logs_by_course_id'
UPDATE_LOG = 'local_webservices_update_log'
ROOM_SCHEDULE = 'local_webservices_get_schedules'
ROOM_BY_CAMPUS = 'local_webservices_get_rooms'
SESSION = 'local_webservices_get_session_detail'
GET_COURSE = 'core_enrol_get_users_courses'
API_KEY = 'secret_key'
DEF_ROLE = [1, 2, 3, 4]
ADMIN_ROLE = [1]


def moodle_res(r):
    if r.status_code == 200:
        result = r.json()
        if result:
            if 'errorcode' in result and result['errorcode']:
                return {}
            return result
    return {}


def moodle_user(username):
    url = f'{HOST}/webservice/rest/server.php'
    params = {
        'moodlewsrestformat': 'json',
        'wstoken': WSTOKEN,
        'wsfunction': USER_INFO,
        'username': username
    }
    r = req.get(url, params=params)
    user = moodle_res(r)
    if user:
        return user[0]
    return {}


def moodle_token(token):
    url = f'{HOST}/webservice/rest/server.php'
    params = {
        'moodlewsrestformat': 'json',
        'wstoken': token,
        'wsfunction': TOKEN_INFO
    }
    r = req.get(url, params=params)
    return moodle_res(r)


def moodle_login(username, password):
    url = f'{HOST}/login/token.php'
    params = {
        'moodlewsrestformat': 'json',
        'service': 'moodle_mobile_app',
        'username': username,
        'password': password
    }
    r = req.get(url, params=params)
    return moodle_res(r)


def verify(args, admin=False):
    if args['token'] == API_KEY:
        return ''

    role = DEF_ROLE
    if admin:
        role = ADMIN_ROLE

    result = moodle_token(args['token'])
    if not result:
        return jsonify({
            'status': 401,
            'message': 'unauthorized request',
            'data': ''
        }), 401

    user = moodle_user(result['username'])
    if not user or user['roleid'] not in role:
        return jsonify({
            'status': 401,
            'message': 'no permission',
            'data': ''
        }), 401

    return ''


def moodle_checkin(session_id, student_id, status, timein=0, timeout=0):
    student_id = moodle_user(student_id)['id']
    url = f'{HOST}/webservice/rest/server.php'
    params = {
        'moodlewsrestformat': 'json',
        'wstoken': WSTOKEN,
        'wsfunction': UPDATE_LOG,
        'sessionid': session_id,
        'studentid': student_id,
        'statusid': status,
        'timein': time_now(),
        'timeout': timeout
    }
    r = req.get(url, params=params)
    return bool(moodle_res(r))


def moodle_room_schedule(room_id, date):
    url = f'{HOST}/webservice/rest/server.php'
    params = {
        'moodlewsrestformat': 'json',
        'wstoken': WSTOKEN,
        'wsfunction': ROOM_SCHEDULE,
        'roomid': room_id,
        'date': date
    }
    r = req.get(url, params=params)
    return moodle_res(r)


def moodle_session(session_id):
    url = f'{HOST}/webservice/rest/server.php'
    params = {
        'moodlewsrestformat': 'json',
        'wstoken': WSTOKEN,
        'wsfunction': SESSION,
        'sessionid': session_id
    }
    r = req.get(url, params=params)
    return moodle_res(r)


def moodle_log(attendance_id):
    url = f'{HOST}/webservice/rest/server.php'
    params = {
        'moodlewsrestformat': 'json',
        'wstoken': WSTOKEN,
        'wsfunction': GET_LOG,
        'attendanceid': attendance_id
    }
    r = req.get(url, params=params)
    return moodle_res(r)


def moodle_student_log(student_id, course_id):
    url = f'{HOST}/webservice/rest/server.php'
    params = {
        'moodlewsrestformat': 'json',
        'wstoken': WSTOKEN,
        'wsfunction': GET_STUDENT_LOG,
        'studentid': student_id,
        'courseid': course_id
    }
    r = req.get(url, params=params)
    user = moodle_res(r)
    if user:
        return user[0]
    return {}


def moodle_log_by_course(course_id):
    url = f'{HOST}/webservice/rest/server.php'
    params = {
        'moodlewsrestformat': 'json',
        'wstoken': WSTOKEN,
        'wsfunction': GET_LOG_BY_COURSE,
        'courseid': course_id
    }
    r = req.get(url, params=params)
    return moodle_res(r)


def moodle_room_by_campus(campus_id):
    url = f'{HOST}/webservice/rest/server.php'
    params = {
        'moodlewsrestformat': 'json',
        'wstoken': WSTOKEN,
        'wsfunction': ROOM_BY_CAMPUS,
        'campus': campus_id
    }
    r = req.get(url, params=params)
    return moodle_res(r)


def moodle_get_course(token, user_id):
    url = f'{HOST}/webservice/rest/server.php'
    params = {
        'moodlewsrestformat': 'json',
        'wstoken': token,
        'wsfunction': GET_COURSE,
        'userid': user_id
    }
    r = req.get(url, params=params)
    return moodle_res(r)
