import pymongo
from flask_pymongo import PyMongo


PASSWORD = 'AdminPass123'
CLUSTER = 'cluster0.qe6sa.mongodb.net'
NAME = 'face_db'
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

    def get_users(self):
        size = self.db.count_documents({})

        if size == 0:
            return [], []

        results = self.db.find()

        ids = [None] * size
        embeds = [[]] * size

        for i in range(size):
            ids[i] = results[i]['id']
            embeds[i] = results[i]['embed']

        return ids, embeds

    def insert(self, user: dict):
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
                        'embed': user['embed']
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
