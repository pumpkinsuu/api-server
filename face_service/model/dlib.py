import face_recognition as fr
from face_service.utilities import *


class Model:
    def __init__(self):
        self.model = fr
        self.tol = 0.37
        self.size = (150, 150)
        self.face_location = [(0, 150, 150, 0)]

    def __preprocess(self, img):
        return resize(img, self.size)

    def get_embed(self, img):
        _img = self.__preprocess(img)
        embed = self.model.face_encodings(_img, self.face_location)[0]
        return embed
