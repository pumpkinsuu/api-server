import pymongo
import numpy as np
from typing import List


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
        faces = [{'id': result['id'], 'data': np.array(result['data'])}
                 for result in results]
        return faces

    def find(self, face_id: int):
        result = self.db.find_one({'id': face_id})
        if result:
            return {
                'id': result['id'],
                'data': np.array(result['data'])
            }
        return {}

    def insert(self, face: dict):
        try:
            self.db.insert_one(face)
            return True
        except Exception as ex:
            print(f'Insert: {ex}')
            return False

    def update(self, face: dict):
        try:
            self.db.update_one(face['id'], {"$set": face['data']})
            return True
        except Exception as ex:
            print(f'Insert: {ex}')
            return False

    def remove(self, face_id: int):
        try:
            self.db.delete_one(face_id)
            return True
        except Exception as ex:
            print(f'Insert: {ex}')
            return False
