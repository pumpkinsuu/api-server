from photo_service.database import DataBase


class PhotoApi:
    def __init__(self, app):
        self.db = DataBase(app)

    def get_user(self, ID):
        user = self.db.get_user(ID)
        if user:
            return 200, user

        return 404, 'username not found'

    def create_user(self, ID, left, right, front):
        if self.db.get_user(ID):
            return 409, 'username already exists'

        if self.db.create({
            'id': ID,
            'left': left,
            'right': right,
            'front': front
        }):
            return 201, 'success'

        return 500, 'internal server error'

    def update_user(self, ID, left, right, front):
        if not self.db.get_user(ID):
            return 404, 'username not registered'

        if self.db.update({
            'id': ID,
            'left': left,
            'right': right,
            'front': front
        }):
            return 200, 'success'

        return 500, 'internal server error'

    def remove_user(self, ID):
        if not self.db.get_user(ID):
            return 404, 'username not registered'

        if self.db.remove(ID):
            return 200, 'success'

        return 500, 'internal server error'
