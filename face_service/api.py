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
    def __init__(self, app, model=1):
        if model == 1:
            from face_service.model import Model
            self.model = Model()
        else:
            from face_service.facenet_model import Model
            self.model = Model()

        self.db = DataBase(app)

    def create_user(self, ID, front, left, right):
        try:
            db_ids, db_embeds = self.db.get_users()

            if self.db.get_user(ID):
                return 409, 'username already exists'

            front_embed = self.model.get_embed(front)
            left_embed = self.model.get_embed(left)
            right_embed = self.model.get_embed(right)

            fl = distance(front_embed, left_embed)
            fr = distance(front_embed, right_embed)

            if fl > self.model.tol or fr > self.model.tol:
                return 400, f'different faces: {fl}, {fr}'

            embed = mean([front_embed, left_embed, right_embed])

            if len(db_embeds):
                db_embeds = np.array(db_embeds)

                idx, dist = find_min(embed, db_embeds)
                if dist < self.model.tol:
                    return 409, 'face already exists'

            if self.db.create({
                'id': ID,
                'embed': embed.tolist()
            }):
                return 201, 'success'

            return 500, 'failed to create'
        except Exception as ex:
            print(f'\n***FaceAPI Create_user error: {ex}***\n')
            return 500, str(ex)

    def update_user(self, ID, front, left, right):
        try:
            db_ids, db_embeds = self.db.get_users()

            if not self.db.get_user(ID):
                return 404, 'username not registered'

            front_embed = self.model.get_embed(front)
            left_embed = self.model.get_embed(left)
            right_embed = self.model.get_embed(right)

            if distance(front_embed, left_embed) > self.model.tol or distance(front_embed, right_embed) > self.model.tol:
                return 400, 'different faces'

            embed = mean([front_embed, left_embed, right_embed])

            if len(db_embeds):
                db_embeds = np.array(db_embeds)
                idx, dist = find_min(embed, db_embeds)
                if dist < self.model.tol and db_ids[idx] != ID:
                    return 409, 'face already exists'

            if self.db.update({
                'id': ID,
                'embed': embed.tolist()
            }):
                return 200, 'success'

            return 500, 'failed to update'
        except Exception as ex:
            print(f'\n***FaceAPI Update_user error: {ex}***\n')
            return 500, str(ex)

    def remove_user(self, ID):
        try:
            if not self.db.get_user(ID):
                return 404, 'username not registered'

            if self.db.remove(ID):
                return 200, 'successful'

            return 500, 'failed to remove'
        except Exception as ex:
            print(f'\n***FaceAPI Remove_user error: {ex}***\n')
            return 500, str(ex)

    def verify(self, image):
        try:
            db_ids, db_embeds = self.db.get_users()
            if not db_ids:
                return 500, 'database empty'

            embed = self.model.get_embed(image)
            idx, dist = find_min(embed, db_embeds)
            if dist <= self.model.tol:
                return 200, db_ids[idx]

            return 404, 0
        except Exception as ex:
            print(f'\n***FaceAPI verify_user error: {ex}***\n')
            return 500, str(ex)

    def get_user(self, ID):
        try:
            user = self.db.get_user(ID)
            if user:
                return 200, 'exist'

            return 404, 'username not found'
        except Exception as ex:
            print(f'\n***FaceAPI Get_user error: {ex}***\n')
            return 500, str(ex)

    def get_users(self):
        try:
            ids, _ = self.db.get_users()
            if len(ids) != 0:
                return 200, ids

            return 500, 'database empty'
        except Exception as ex:
            print(f'\n***FaceAPI Get_users error: {ex}***\n')
            return 500, str(ex)
