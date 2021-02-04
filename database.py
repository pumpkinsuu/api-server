import pymongo
from flask_pymongo import PyMongo


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DataBase(metaclass=Singleton):
    def __init__(self, app, dbname, password, cluster, collection='main'):
        app.config['MONGO_URI'] = f"mongodb+srv://admin:{password}@{cluster}/" \
                                  f"{dbname}?retryWrites=true&w=majority"
        self.db = PyMongo(app).db[collection]

        if self.db.count_documents({}) == 0:
            self.db.create_index([('id', pymongo.ASCENDING)], unique=True)

    def get_user(self, user_id: int):
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

    def remove(self, user_id: int):
        try:
            self.db.delete_one({'id': user_id})

            return True
        except Exception as ex:
            print(f'Delete: {ex}')
            return False
