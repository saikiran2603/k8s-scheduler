import bson


class SchedulerBackend:
    def __init__(self):
        """
        Initialize connection to MongoDb backend
        """
        # Check if database and collections exists if not create them
        # list_coll = connection.list_collection_names()
        # for collection in list_coll:
        #     print(collection)

    def create_schedule(self, db_connection, schedule_rec):
        res = db_connection.find_one({"schedule_name": schedule_rec['schedule_name']})
        if res is None:
            res = db_connection.insert_one(schedule_rec)
            return res.inserted_id
        else:
            raise Exception("Schedule Already exists ")

    def disable_schedule(self, db_connection, schedule_id):
        disable_schedule = {"$set": {"schedule_enabled": 0}}
        res = db_connection.update_one(filter={'_id': bson.objectid.ObjectId(schedule_id)},
                                       update=disable_schedule)
        return res.modified_count

    def purge_schedule(self, db_connection, schedule_id):
        res = db_connection.delete_one(filter={'_id': bson.objectid.ObjectId(schedule_id)})
        return res.deleted_count
