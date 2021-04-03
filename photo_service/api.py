from photo_service.database import DataBase


class PhotoApi:
    def __init__(self, app):
        self.db = DataBase(app)

    def get_user(self, ID):
        user = self.db.get_user(ID)
        if user:
            return 200, user

        return 404, 'Username not found'

    def create_user(self, ID, left, right, front):
        if self.db.get_user(ID):
            return 409, 'Username already exists'

        if self.db.create({
            'id': ID,
            'left': left,
            'right': right,
            'front': front
        }):
            return 201, 'Successful'

        return 500, 'Internal Server Error'

    def update_user(self, ID, left, right, front):
        if not self.db.get_user(ID):
            return 404, 'Username not registered'

        if self.db.update({
            'id': ID,
            'left': left,
            'right': right,
            'front': front
        }):
            return 200, 'Successful'

        return 500, 'Internal Server Error'

    def remove_user(self, ID):
        if not self.db.get_user(ID):
            return 404, 'Username not registered'

        if self.db.remove(ID):
            return 200, 'Successful'

        return 500, 'Internal Server Error'
