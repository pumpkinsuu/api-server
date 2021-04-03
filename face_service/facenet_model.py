import tensorflow as tf
import numpy as np


class Model:
    def __init__(self, model_path, tol=0.8):
        self.tol = tol
        self.size = (160, 160, 3)
        self.graph = self.__load_pb(model_path)
        self.sess = tf.compat.v1.Session(graph=self.graph)
        self.input = self.graph.get_tensor_by_name('input:0')
        self.output = self.graph.get_tensor_by_name('embeddings:0')
        self.placeholder = self.graph.get_tensor_by_name('phase_train:0')

    @staticmethod
    def __load_pb(path):
        with tf.compat.v1.gfile.GFile(path, "rb") as f:
            graph_def = tf.compat.v1.GraphDef()
            graph_def.ParseFromString(f.read())
        with tf.Graph().as_default() as graph:
            tf.import_graph_def(graph_def, name='')
            return graph

    @staticmethod
    def __prewhiten(x):
        mean = np.mean(x)
        std = np.std(x)
        std_adj = np.maximum(std, 1.0 / np.sqrt(x.size))
        y = np.multiply(np.subtract(x, mean), 1 / std_adj)
        return y

    @staticmethod
    def __l2_normalize(x, axis=-1, epsilon=1e-10):
        output = x / np.sqrt(np.maximum(np.sum(np.square(x), axis=axis, keepdims=True), epsilon))
        return output

    def __preprocess(self, img):
        return self.__prewhiten(np.array(img.resize(self.size)))

    def get_embed(self, img):
        data = [self.__preprocess(img)]
        feed_dict = {self.input: data, self.placeholder: False}

        embed = self.sess.run(self.output, feed_dict=feed_dict)[0]
        embed = self.__l2_normalize(embed)

        return embed

