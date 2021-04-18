from flask import Flask, jsonify
from flask_cors import CORS
from flask_ngrok import run_with_ngrok
import argparse
import os

from face_service.api import FaceAPI
from photo_service.api import PhotoAPI
from face.face import create_face_bp
from api.api import api_bp

app = Flask(__name__, static_url_path='/data', static_folder='data')
CORS(app)


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({
        'status': 404,
        'message': 'requested URL not found',
        'data': ''
    }), 404


@app.errorhandler(405)
def method_not_allow(e):
    return jsonify({
        'status': 405,
        'message': 'wrong URL or method',
        'data': ''
    }), 405


def main(argv):
    if argv.remote == 1:
        run_with_ngrok(app)
    if argv.debug == 1:
        app.config["DEBUG"] = True

    if not os.path.isdir('data'):
        os.mkdir('data')

    face_api = FaceAPI(app, argv.model)
    photo_api = PhotoAPI(app)

    face_bp = create_face_bp(face_api, photo_api)
    CORS(face_bp)
    CORS(api_bp)

    app.register_blueprint(face_bp, url_prefix='/face')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.run()


if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('--remote', type=int, default=0)
    parse.add_argument('--debug', type=int, default=0)
    parse.add_argument('--model', type=int, default=1
                       , help='1: facenet, 2: dlib')
    args = parse.parse_args()
    main(args)
