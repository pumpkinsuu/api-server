import numpy as np
import pymongo


class DataBase:
    def __init__(self, dbname, password, collection='main'):
        client = pymongo.MongoClient(f"mongodb+srv://admin:{password}@cluster0.qe6sa.mongodb.net/"
                                     f"{dbname}?retryWrites=true&w=majority")
        db = client[dbname][collection]
        if db.count_documents({}) == 0:
            db.create_index([('id', pymongo.ASCENDING)], unique=True)

        self.db = db

    def find_all(self):
        results = self.db.find().sort('id')
        users = [{'id': result['id'], 'data': result['data']}
                 for result in results]

        return users

    def get_data(self):
        results = self.db.find().sort('id')

        ids = []
        embeds = []
        for result in results:
            for embed in result['data']:
                ids.append(result['id'])
                embeds.append(embed)

        return np.array(ids), np.array(embeds)

    def find(self, user_id: int):
        result = self.db.find_one({'id': user_id})
        if result:
            return {
                'id': result['id'],
                'data': np.array(result['data'])
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
            self.db.update_one(user['id'], {"$set": user['data']})
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
