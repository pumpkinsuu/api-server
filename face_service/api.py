from face_service.database import DataBase
import numpy as np

from utilities import load_img


def mean(arr):
    return np.mean(arr, 0)


def distance(a, b, axis=None):
    return np.sqrt(np.sum((a - b) ** 2, axis))


def find_min(x, arr):
    dist = distance(x, arr, 1)
    idx = np.argmin(dist)
    return idx, dist[idx]


class FaceAPI:
    def __init__(self,
                 app,
                 model=1):
        if model == 1:
            from face_service.model.facenet import Model
            self.model = Model()
        else:
            from face_service.model.dlib import Model
            self.model = Model()

        self.db = DataBase(app)

    def create_user(self,
                    collection,
                    user_id,
                    front,
                    left,
                    right):
        try:
            db_ids, db_embeds = self.db.get_users(collection)

            if self.db.get_user(collection, user_id):
                return 409, 'username already exists'

            front_embed = self.model.get_embed(
                load_img(front)
            )
            left_embed = self.model.get_embed(
                load_img(left)
            )
            right_embed = self.model.get_embed(
                load_img(right)
            )

            if distance(front_embed, left_embed) > self.model.tol or distance(front_embed,
                                                                              right_embed) > self.model.tol:
                return 400, f'different faces'

            embed = mean([front_embed, left_embed, right_embed])

            if len(db_embeds):
                db_embeds = np.array(db_embeds)

                idx, dist = find_min(embed, db_embeds)
                if dist < self.model.tol:
                    return 409, f'face already exists {db_ids[idx]}'

            if self.db.create(collection, {
                'id': user_id,
                'embed': embed.tolist()
            }):
                return 201, 'success'

            return 500, 'failed to create'
        except Exception as ex:
            print(f'\n***FaceAPI Create_user error: {ex}***\n')
            return 500, str(ex)

    def update_user(self,
                    collection,
                    user_id,
                    front,
                    left,
                    right):
        try:
            db_ids, db_embeds = self.db.get_users(collection)

            if not self.db.get_user(collection, user_id):
                return 404, 'username not registered'

            front_embed = self.model.get_embed(
                load_img(front)
            )
            left_embed = self.model.get_embed(
                load_img(left)
            )
            right_embed = self.model.get_embed(
                load_img(right)
            )

            if distance(front_embed, left_embed) > self.model.tol or distance(front_embed,
                                                                              right_embed) > self.model.tol:
                return 400, 'different faces'

            embed = mean([front_embed, left_embed, right_embed])

            if len(db_embeds):
                db_embeds = np.array(db_embeds)
                idx, dist = find_min(embed, db_embeds)
                if dist < self.model.tol and db_ids[idx] != user_id:
                    return 409, f'face already exists {db_ids[idx]}'

            if self.db.update(
                    collection,
                    user_id,
                    {'embed': embed.tolist()}
            ):
                return 200, 'success'

            return 500, 'failed to update'
        except Exception as ex:
            print(f'\n***FaceAPI Update_user error: {ex}***\n')
            return 500, str(ex)

    def remove_user(self,
                    collection,
                    user_id):
        if not self.db.get_user(collection, user_id):
            return 404, 'username not registered'

        if self.db.remove(collection, user_id):
            return 200, 'successful'

        return 500, 'failed to remove'

    def verify(self,
               collection,
               image):
        try:
            db_ids, db_embeds = self.db.get_users(collection)
            if not db_ids:
                return 500, 'database empty'

            embed = self.model.get_embed(
                load_img(image)
            )
            idx, dist = find_min(embed, db_embeds)

            if dist <= self.model.tol:
                return 200, db_ids[idx]

            return 404, ''
        except Exception as ex:
            print(f'\n***FaceAPI verify_user error: {ex}***\n')
            return 500, str(ex)

    def distance(self, img1, img2):
        try:
            emb1 = self.model.get_embed(
                load_img(img1)
            )
            emb2 = self.model.get_embed(
                load_img(img2)
            )
            return 200, distance(emb1, emb2)

        except Exception as ex:
            print(f'\n***FaceAPI distance error: {ex}***\n')
            return 500, str(ex)

    def get_user(self,
                 collection,
                 user_id):
        user = self.db.get_user(collection, user_id)
        if user:
            return 200, 'exist'

        return 404, 'username not found'

    def rename_user(self,
                    collection,
                    user_id,
                    new_id):
        if self.db.get_user(collection, user_id):
            return 404, 'username not found'

        if self.db.update(
                collection,
                user_id,
                {'id': new_id}
        ):
            return 200, 'success'

        return 500, 'failed to update'

    def get_users(self, collection):
        ids, _ = self.db.get_users(collection)
        if len(ids) != 0:
            return 200, ids

        return 500, 'database empty'

    def count_collection(self, collection):
        sz = self.db.count(collection)
        if sz == -1:
            return 500, 'database error'

        return 200, sz

    def rename_collection(self,
                          collection,
                          name):
        if self.db.count(collection) == 0:
            return 500, 'collection empty'

        self.db.rename(collection, name)
        return 200, 'success'

    def drop_collection(self, collection):
        return 200, self.db.drop(collection)
