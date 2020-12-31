import tensorflow as tf


class Model:
    def __init__(self, model_path):
        self.graph = self.__load_pb(model_path)
        self.sess = tf.compat.v1.Session(graph=self.graph)
        self.input = self.graph.get_tensor_by_name('img_inputs:0')
        self.output = self.graph.get_tensor_by_name('embeddings:0')

    @staticmethod
    def __load_pb(path):
        with tf.compat.v1.gfile.GFile(path, "rb") as f:
            graph_def = tf.compat.v1.GraphDef()
            graph_def.ParseFromString(f.read())
        with tf.Graph().as_default() as graph:
            tf.import_graph_def(graph_def, name='')
            return graph

    def get_embed(self, data):
        embeds = self.sess.run(self.output, feed_dict={self.input: data})
        return embeds

