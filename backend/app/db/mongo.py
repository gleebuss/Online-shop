from pymongo import MongoClient
from pymongo.collection import Collection
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
MONGO_DB_NAME = "db"

client = MongoClient(MONGO_URL)
db = client[MONGO_DB_NAME]
products_collection: Collection = db["products"]

def get_mongo_collection():
    return products_collection
