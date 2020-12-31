from keras.models import load_model


class Model:
    def __init__(self, model_path):
        self.model = load_model(model_path)

    def get_embed(self, data):
        embeds = self.model.predict_on_batch(data)
        return embeds
