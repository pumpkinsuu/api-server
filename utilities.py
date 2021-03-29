from PIL import Image
from flask import jsonify
import base64
import io


def load_img_base64(file):
    img = Image.open(io.BytesIO(base64.b64decode(file)))
    return img


def load_img(file):
    img = Image.open(file)
    return img


def encode_img(file):
    with open(file, 'rb') as f:
        return base64.b64encode(f.read())


# Add CORS to response header
def res_cors(data):
    res = jsonify(data)
    res.headers.add("Access-Control-Allow-Origin", "*")
    return res



