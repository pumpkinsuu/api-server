import face_recognition as fr


class Model:
    def __init__(self, tol=0.37):
        self.model = fr
        self.tol = tol
        self.size = (150, 150, 3)

    def get_embed(self, data):
        embed = self.model.face_encodings(data, [(0, 150, 150, 0)], model='large')[0]
        return embed
