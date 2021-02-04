import numpy as np
from PIL import Image


def mean(arr):
    return np.mean(arr, 0)


def distance(a, b):
    return np.sqrt(np.sum((a - b)**2, 1))


def find_min(x, arr):
    dist = distance(x, arr)
    idx = np.argmin(dist)
    return idx, dist[idx]


def load_img(file):
    img = Image.open(file)
    return np.array(img)

