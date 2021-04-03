import pymongo
from flask_pymongo import PyMongo


PASSWORD = 'AdminPass123'
CLUSTER = 'facecluster.oy4x6.mongodb.net'
NAME = 'photo_db'
COLLECTION = 'main'


class DataBase:
    def __init__(self, app):
        app.config['MONGO_URI'] = f"mongodb+srv://admin:{PASSWORD}@{CLUSTER}/" \
                                  f"{NAME}?retryWrites=true&w=majority"
        self.db = PyMongo(app).db[COLLECTION]

        if self.db.count_documents({}) == 0:
            self.db.create_index([('id', pymongo.ASCENDING)], unique=True)

    def get_user(self, user_id):
        return self.db.find_one({'id': user_id})

    def create(self, user: dict):
        try:
            self.db.insert_one(user)

            return True
        except Exception as ex:
            print(f'Insert: {ex}')
            return False

    def update(self, user: dict):
        try:
            self.db.update_one(
                {
                    'id': user['id']
                },
                {
                    "$set": {
                        'left': user['left'],
                        'right': user['right'],
                        'front': user['front']
                    }
                }
            )

            return True
        except Exception as ex:
            print(f'Update: {ex}')
            return False

    def remove(self, user_id):
        try:
            self.db.delete_one({'id': user_id})

            return True
        except Exception as ex:
            print(f'Delete: {ex}')
            return False
