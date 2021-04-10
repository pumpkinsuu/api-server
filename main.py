from utilities import res_cors
from flask import Flask
from flask_ngrok import run_with_ngrok
import argparse
import os

from face.face import create_face_bp
from api.api import api_bp


app = Flask(__name__, static_url_path='/data', static_folder='data')


@app.errorhandler(404)
def page_not_found(e):
    print(e)
    return res_cors({
        'code': 404,
        'message': 'Page not found',
        'data': ''
    }), 404


def main(argv):
    if argv.remote == 1:
        run_with_ngrok(app)
    if argv.debug == 1:
        app.config["DEBUG"] = True

    if not os.path.isdir('data'):
        os.mkdir('data')

    face_bp = create_face_bp(app, argv.model)
    app.register_blueprint(face_bp, url_prefix='/face')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.run()


if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('--remote', type=int, default=0)
    parse.add_argument('--debug', type=int, default=0)
    parse.add_argument('--model', type=int, default=1
                       , help='1: dlib, 2: facenet')
    args = parse.parse_args()
    main(args)
