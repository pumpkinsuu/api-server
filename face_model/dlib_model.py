import face_recognition as fr


class Model:
    def __init__(self):
        self.model = fr
        self.tol = 0.37
        self.size = (150, 150, 3)
        self.face_location = [(0, 150, 150, 0)]

    def get_embed(self, img):
        embed = self.model.face_encodings(img, self.face_location)[0]
        return embed
