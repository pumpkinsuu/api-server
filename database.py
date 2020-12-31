import numpy as np
import pymongo


class DataBase:
    def __init__(self, dbname, password, cluster, collection='main'):
        client = pymongo.MongoClient(f"mongodb+srv://admin:{password}@{cluster}/"
                                     f"{dbname}?retryWrites=true&w=majority")
        db = client[dbname][collection]
        if db.count_documents({}) == 0:
            db.create_index([('id', pymongo.ASCENDING)], unique=True)

        self.db = db

    def get_users(self, limit=0, offset=0):
        sz = self.db.count_documents({})
        if sz == 0:
            return [], [], 0

        results = self.db.find().sort('id').limit(limit).skip(offset)

        total = np.min(sz, limit)

        ids = np.empty([total, 1])
        embeds = np.empty([total, 128])

        for i in range(total):
            ids[i] = results[i]['id']
            embeds[i] = results[i]['embed']

        return ids, embeds, sz

    def get_user(self, user_id: int):
        result = self.db.find_one({'id': user_id})
        if result:
            return {
                'id': result['id'],
                'embed': result['embed'],
                'photo': result['photo']
            }
        return {}

    def find_all(self, limit=0, offset=0):
        sz = self.db.count_documents({})
        if sz == 0:
            return [], 0

        results = self.db.find().sort('id').limit(limit).skip(offset)
        users = [
            {
                'id': result['id'],
                'photo': result['photo']
            }
            for result in results
        ]

        return users, sz

    def find(self, user_id: int):
        result = self.db.find_one({'id': user_id})
        if result:
            return {
                'id': result['id'],
                'photo': result['photo']
            }
        return {}

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
                        'embed': user['embed'],
                        'photo': user['photo']
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
