from flask import Flask
from flask_cors import CORS
import argparse
import os

from face_service.api import FaceAPI
from face_service.router import create_api_bp

app = Flask(__name__, static_url_path='/data', static_folder='data')
CORS(app)


@app.errorhandler(404)
def page_not_found(e):
    return 'not found', 404


def main(argv):
    if not os.path.isdir('data'):
        os.mkdir('data')

    face_api = FaceAPI(app, argv.model)

    api_bp = create_api_bp(face_api)
    CORS(api_bp)

    app.register_blueprint(api_bp)
    app.run()


if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('--model', type=int, default=1
                       , help='1: facenet, 2: dlib')
    args = parse.parse_args()
    main(args)
