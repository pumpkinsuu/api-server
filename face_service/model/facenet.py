import tensorflow as tf
from face_service.utilities import *


def load_pb(path):
    with tf.compat.v1.gfile.GFile(path, "rb") as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def, name='')
        return graph


class Model:
    def __init__(self):
        self.tol = 0.7
        self.size = (160, 160)
        self.graph = load_pb('data/facenet.pb')
        self.sess = tf.compat.v1.Session(graph=self.graph)
        self.input = self.graph.get_tensor_by_name('input:0')
        self.output = self.graph.get_tensor_by_name('embeddings:0')
        self.placeholder = self.graph.get_tensor_by_name('phase_train:0')

    def __preprocess(self, img):
        return prewhiten(resize(img, self.size))

    def get_embed(self, img):
        data = [self.__preprocess(img)]
        feed_dict = {self.input: data, self.placeholder: False}

        embed = self.sess.run(self.output, feed_dict=feed_dict)[0]
        embed = l2_normalize(embed)

        return embed
