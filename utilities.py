from PIL import Image
from base64 import b64decode
from io import BytesIO
import time


def load_img(file):
    img = Image.open(BytesIO(b64decode(file)))
    return img


def time_now():
    return int(time.time())


# Add CORS to response header
"""def res_cors(data):
    res = jsonify(data)
    res.headers.add("Access-Control-Allow-Origin", "*")
    return res"""

