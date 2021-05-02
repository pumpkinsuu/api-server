from photo_service.database import DataBase
from utilities import time_now

class PhotoAPI:
    def __init__(self, app):
        self.db = DataBase(app)

    def get_user(self,
                 collection,
                 user_id):
        user = self.db.get_user(collection, user_id)
        if user:
            return 200, user

        return 404, 'username not found'

    def create_user(self,
                    collection,
                    user_id,
                    left,
                    right,
                    front):
        if self.db.get_user(collection, user_id):
            return 409, 'username already exists'

        if self.db.create(collection, {
            'id': user_id,
            'left': left,
            'right': right,
            'front': front
        }):
            return 201, 'success'

        return 500, 'internal server error'

    def create_feedback(self,
                        collection,
                        user_id,
                        room_id,
                        image):
        if not self.db.get_user(collection, user_id):
            return 404, 'username not registered'

        if self.db.create(f'feedback_{collection}', {
            'id': f'{time_now()}_{user_id}',
            'userId': user_id,
            'roomId': room_id,
            'image': image
        }):
            return 200, 'success'

        return 500, 'internal server error'

    def update_user(self,
                    collection,
                    user_id,
                    left,
                    right,
                    front):
        if not self.db.get_user(collection, user_id):
            return 404, 'username not registered'

        if self.db.update(collection, {
            'id': user_id,
            'left': left,
            'right': right,
            'front': front
        }):
            return 200, 'success'

        return 500, 'internal server error'

    def remove_user(self,
                    collection,
                    user_id):
        if not self.db.get_user(collection, user_id):
            return 404, 'username not registered'

        if self.db.remove(collection, user_id):
            return 200, 'success'

        return 500, 'internal server error'

    def count_collection(self,
                         collection):
        sz = self.db.count(collection)
        if sz == -1:
            return 500, 'database error'

        return 200, sz

    def rename_collection(self,
                          collection,
                          name):
        self.db.rename(collection, name)

        return 200, 'success'

    def drop_collection(self,
                        collection):
        return 200, self.db.drop(collection)
