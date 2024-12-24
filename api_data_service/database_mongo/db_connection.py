from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import json
from api_data_service.config import MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD, MONGO_DB_NAME


class MongoDBConnection:
    def __init__(self):
        try:
            connection_string = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
            print(f"Trying to connect to MongoDB with: {connection_string}")
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            # Test the connection
            self.client.server_info()
            print("Successfully connected to MongoDB")
            self.db = self.client[MONGO_DB_NAME]
            self.collection = self.db["event_collection"]
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise

    def save_json_to_mongo(self, json_data):
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        result = self.collection.insert_one(json_data)
        print(f"Document inserted with ID: {str(result.inserted_id)}")
