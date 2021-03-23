import numpy as np
from PIL import Image
from flask import jsonify
import base64


def mean(arr):
    return np.mean(arr, 0)


def distance(a, b, axis=None):
    return np.sqrt(np.sum((a - b) ** 2, axis))


def find_min(x, arr):
    dist = distance(x, arr, 1)
    idx = np.argmin(dist)
    return idx, dist[idx]


def load_img(file):
    img = Image.open(file)
    return np.array(img)


def encode_img(file):
    with open(file, 'rb') as f:
        return base64.b64encode(f.read())


def save_img(path, img):
    im = Image.fromarray(img)
    im.save(path)


# Add CORS to response header
def res_cors(data):
    res = jsonify(data)
    res.headers.add("Access-Control-Allow-Origin", "*")
    return res
