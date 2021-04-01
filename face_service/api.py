from face_service.model import Model
from face_service.database import DataBase
import numpy as np


def mean(arr):
    return np.mean(arr, 0)


def distance(a, b, axis=None):
    return np.sqrt(np.sum((a - b) ** 2, axis))


def find_min(x, arr):
    dist = distance(x, arr, 1)
    idx = np.argmin(dist)
    return idx, dist[idx]


class FaceAPI:
    def __init__(self, app):
        self.model = Model()
        self.db = DataBase(app)

    def create_user(self, ID, front, left, right):
        db_ids, db_embeds = self.db.get_users()

        if ID in db_ids:
            return 409, 'Username already exists'

        front_embed = self.model.get_embed(front)
        left_embed = self.model.get_embed(left)
        right_embed = self.model.get_embed(right)

        if distance(front_embed, left_embed) > self.model.tol or distance(front_embed, right_embed) > self.model.tol:
            return 400, 'Different faces'

        embed = mean([front_embed, left_embed, right_embed])

        db_embeds = np.array(db_embeds)
        idx, dist = find_min(embed, db_embeds)
        if dist < self.model.tol:
            return 409, 'Face already exists'

        if self.db.insert({
            'id': ID,
            'embed': embed.tolist()
        }):
            return 201, 'Successful'

        return 500, 'Internal Server Error'

    def update_user(self, ID, front, left, right):
        db_ids, db_embeds = self.db.get_users()

        if ID not in db_ids:
            return 404, 'Username not registered'

        front_embed = self.model.get_embed(front)
        left_embed = self.model.get_embed(left)
        right_embed = self.model.get_embed(right)

        if distance(front_embed, left_embed) > self.model.tol or distance(front_embed, right_embed) > self.model.tol:
            return 400, 'Different faces'

        embed = mean([front_embed, left_embed, right_embed])

        db_embeds = np.array(db_embeds)
        idx, dist = find_min(embed, db_embeds)
        if dist < self.model.tol and db_ids[idx] != ID:
            return 409, 'Face already exists'

        if self.db.update({
            'id': ID,
            'embed': embed.tolist()
        }):
            return 200, 'Successful'

        return 500, 'Internal Server Error'

    def remove_user(self, ID):
        ids, _ = self.db.get_users()

        if ID not in ids:
            return 404, 'Username not registered'

        if self.db.remove(ID):
            return 200, 'Successful'

        return 500, 'Internal Server Error'

    def verify(self, image):
        db_ids, db_embeds = self.db.get_users()
        if not db_ids:
            return 500, 'Database empty'

        embed = self.model.get_embed(image)
        idx, dist = find_min(embed, db_embeds)
        if dist <= self.model.tol:
            return 200, db_ids[idx]

        return 404, 0

    def get_user(self, ID):
        user = self.db.get_user(ID)
        if user:
            return 200, 'Exist'

        return 404, 'Username not found'

    def get_users(self):
        ids, _ = self.db.get_users()
        if len(ids) != 0:
            return 200, ids

        return 500, 'Database empty'
