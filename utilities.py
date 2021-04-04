from PIL import Image
from flask import jsonify
import base64
import io


def load_img(file):
    img = Image.open(io.BytesIO(base64.b64decode(file)))
    return img


# Add CORS to response header
def res_cors(data):
    res = jsonify(data)
    res.headers.add("Access-Control-Allow-Origin", "*")
    return res



