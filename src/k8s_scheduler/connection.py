from pymongo import MongoClient


class ConnectionManager:

    def __init__(self, db_name, **kwargs):
        print("Initiating connection with backend database ")
        mongo_client = MongoClient(**kwargs)
        self.handle = mongo_client[db_name]

    def get_connection(self):
        return self.handle
