import numpy as np
from PIL import Image
import os


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


def save_img(path, img_arr):
    img = Image.fromarray(img_arr)
    img.save(path)


def save_photo(user_path, images, host):
    if not os.path.isdir(user_path):
        os.mkdir(user_path)

    i = 0
    photo = []

    for img in images:
        save_img(f'{user_path}/{i}.jpg', img)
        photo.append(f'https://{host}/{user_path}/{i}.jpg')
        i += 1

    return photo
