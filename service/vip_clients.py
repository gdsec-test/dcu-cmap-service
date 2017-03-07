from pymongo import MongoClient


class VipClients(object):

    def __init__(self, db_host='localhost', db_port=27017, db='local', table='blacklist'):
        client = MongoClient(db_host, db_port)
        db = client[db]
        self.collection = db[table]

    def query_entity(self, entity_id):
        db_key = 'entity'
        result = self.collection.find_one({db_key: str(entity_id)})
        # If the shopper id exists, they are VIP
        vip_status = True
        if result is None:
            vip_status = False
        return vip_status
