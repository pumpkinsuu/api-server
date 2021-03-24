import requests as req
from utilities import *


HOST = 'http://localhost'
WSTOKEN = 'e7566fcd661773f232f9b5a1fd4bdc8e'
INFO_TOKEN = 'core_webservice_get_site_info'
ROLE_ID = 'local_webservices_get_roles'
GET_REPORT = ''
GET_REPORT_STUDENT = ''
POST_REPORT = 'local_webservices_update_log'
ROOM_SCHEDULE = ''
SESSION = ''
GET_USER = ''
SECRET = 'secret_key'


def verify(args, role=None):
    if 'token' not in args:
        return res_cors({
            'code': 400,
            'message': 'Bad request',
            'data': ''
        }), 400

    if args['token'] == SECRET:
        return ''

    if role is None:
        role = ['teacher', 'admin']

    url = f'{HOST}/webservice/rest/server.php' \
          f'?moodlewsrestformat=json' \
          f'&service=moodle_mobile_app' \
          f'&wstoken={WSTOKEN}' \
          f'&wsfunction={INFO_TOKEN}' \
          f'&token={args["token"]}'
    r = req.post(url)

    if r.status_code != 200:
        return res_cors({
            'code': 401,
            'message': 'Unauthorized request',
            'data': ''
        }), 401

    result = r.json()['role']

    if result not in role:
        return res_cors({
            'code': 401,
            'message': 'No permission',
            'data': ''
        }), 401

    return ''
