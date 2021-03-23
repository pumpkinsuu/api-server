import requests as req
from utilities import *


HOST = 'http://localhost:8888/moodle310'
WSTOKEN = '328f1791e140b1fe5c3632d71c1bbf9f'
TOKEN = 'core_webservice_get_site_info'
GET_REPORT = ''
POST_REPORT = 'local_wsgetreports_update_status'
ROOM_SCHEDULE = ''
SESSION = ''
LIST_USER = ''
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
        role = [1, 2]

    url = f'{HOST}/webservice/rest/server.php' \
          f'?moodlewsrestformat=json' \
          f'&service=moodle_mobile_app' \
          f'&wstoken={WSTOKEN}' \
          f'&wsfunction={TOKEN}' \
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
