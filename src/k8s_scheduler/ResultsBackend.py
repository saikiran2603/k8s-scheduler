class ResultBackend:

    def __init__(self):
        pass

    def insert_result_record(self, result_db_collection, rec):
        result_db_collection.insert_one(rec)
        return True

    def get_results(self):
        pass