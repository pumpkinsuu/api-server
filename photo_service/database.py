import pymongo
from flask_pymongo import PyMongo


PASSWORD = 'AdminPass123'
CLUSTER = 'facecluster.oy4x6.mongodb.net'
NAME = 'photo_db'


class DataBase:
    def __init__(self,
                 app):
        app.config['MONGO_URI'] = f"mongodb+srv://admin:{PASSWORD}@{CLUSTER}/" \
                                  f"{NAME}?retryWrites=true&w=majority"
        self.db = PyMongo(app).db

    def get_user(self,
                 collection,
                 user_id):
        return self.db[collection].find_one({'id': user_id})

    def create(self,
               collection,
               user):
        try:
            if self.db[collection].count_documents({}) == 0:
                self.db[collection].create_index([('id', pymongo.TEXT)], unique=True)

            self.db[collection].insert_one(user)

            return True
        except Exception as ex:
            print(f'Insert: {ex}')
            return False

    def update(self,
               collection,
               user):
        try:
            self.db[collection].update_one(
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

    def remove(self,
               collection,
               user_id):
        try:
            self.db[collection].delete_one({'id': user_id})

            return True
        except Exception as ex:
            print(f'Delete: {ex}')
            return False

    def count(self,
              collection):
        try:
            return self.db[collection].count_documents({})
        except Exception as ex:
            print(f'Count: {ex}')
            return -1

    def rename(self,
               collection,
               name):
        try:
            self.db[collection].rename(name)

            return True
        except Exception as ex:
            print(f'Rename: {ex}')
            return False

    def drop(self,
             collection):
        try:
            return self.db.drop_collection(collection)
        except Exception as ex:
            print(f'Drop: {ex}')
            return False
