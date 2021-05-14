from flask import Flask
from flask_cors import CORS
from flask_ngrok import run_with_ngrok
import argparse
import os

from face_service.api import FaceAPI
from face_service.router import create_api_bp

PORT = 5001

app = Flask(__name__)
CORS(app)


@app.errorhandler(404)
def page_not_found(e):
    return 'not found', 404


def main(argv):
    if not os.path.isdir('data'):
        os.mkdir('data')

    if argv.remote == 1:
        run_with_ngrok(app)

    if argv.debug == 1:
        app.config["DEBUG"] = True

    face_api = FaceAPI(app, argv.model)

    api_bp = create_api_bp(face_api)
    CORS(api_bp)

    app.register_blueprint(api_bp)
    app.run(port=PORT)


if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('--remote', type=int, default=0)
    parse.add_argument('--debug', type=int, default=0)
    parse.add_argument('--model', type=int, default=1
                       , help='1: facenet, 2: dlib')
    args = parse.parse_args()
    main(args)
