import face_recognition as fr
import numpy as np


def rgba2rgb(rgba):
    row, col, ch = rgba.shape

    if ch == 3:
        return rgba

    rgb = np.zeros((row, col, 3), dtype='float32')
    r, g, b, a = rgba[:, :, 0], rgba[:, :, 1], rgba[:, :, 2], rgba[:, :, 3]

    a = np.asarray(a, dtype='float32') / 255.0

    R, G, B = (255, 255, 255)

    rgb[:, :, 0] = r * a + (1.0 - a) * R
    rgb[:, :, 1] = g * a + (1.0 - a) * G
    rgb[:, :, 2] = b * a + (1.0 - a) * B

    return np.asarray(rgb, dtype='uint8')


class Model:
    def __init__(self):
        self.model = fr
        self.tol = 0.37
        self.size = (150, 150)
        self.face_location = [(0, 150, 150, 0)]

    def __preprocess(self, img):
        _img = np.array(img.resize(self.size))
        return rgba2rgb(_img)

    def get_embed(self, img):
        _img = self.__preprocess(img)
        embed = self.model.face_encodings(_img, self.face_location)[0]
        return embed
