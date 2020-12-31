import face_recognition as fr


class Model:
    def __init__(self):
        self.model = fr

    def get_embed(self, data):
        embeds = self.model.face_encodings(data)
        return embeds
