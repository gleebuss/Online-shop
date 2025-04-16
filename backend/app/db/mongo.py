from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from app.schemas.user_profile import UserProfileOut, UserProfileCreate, UserProfileUpdate
from app.schemas.cart import CartItem, CartOut
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
MONGO_DB_NAME = "db"

client = MongoClient(MONGO_URL)
db = client[MONGO_DB_NAME]
products_collection: Collection = db["products"]
COLLECTION = "user_profiles"
CARTS_COLLECTION = "carts"
PROMO_COLLECTION = "promotions"

def get_mongo_db() -> Database:
    return db

def get_mongo_collection():
    return products_collection

def get_user_profile(db: Database, customer_id: str) -> UserProfileOut | None:
    doc = db[COLLECTION].find_one({"customer_id": customer_id})
    return UserProfileOut(**doc) if doc else None


def create_user_profile(db: Database, data: UserProfileCreate) -> UserProfileOut:
    db[COLLECTION].insert_one(data.dict())
    return get_user_profile(db, data.customer_id)


def update_user_profile(db: Database, customer_id: str, update_data: dict) -> UserProfileOut:
    db[COLLECTION].update_one({"customer_id": customer_id}, {"$set": update_data})
    return get_user_profile(db, customer_id)


def push_to_list(db: Database, customer_id: str, field: str, value: int):
    db[COLLECTION].update_one({"customer_id": customer_id}, {"$addToSet": {field: value}})


def remove_from_list(db: Database, customer_id: str, field: str, value: int):
    db[COLLECTION].update_one({"customer_id": customer_id}, {"$pull": {field: value}})

def get_cart(db: Database, customer_id: str) -> CartOut | None:
    doc = db[CARTS_COLLECTION].find_one({"customer_id": customer_id})
    if doc:
        return CartOut(customer_id=doc["customer_id"], items=doc.get("items", []))
    return None


def add_to_cart(db: Database, customer_id: str, item: dict):
    db[CARTS_COLLECTION].update_one(
        {"customer_id": customer_id},
        {"$addToSet": {"items": item}},
        upsert=True
    )


def remove_from_cart(db: Database, customer_id: str, product_id: int):
    db[CARTS_COLLECTION].update_one(
        {"customer_id": customer_id},
        {"$pull": {"items": {"product_id": product_id}}}
    )


def clear_cart(db: Database, customer_id: str):
    db[CARTS_COLLECTION].update_one(
        {"customer_id": customer_id},
        {"$set": {"items": []}}
    )

def get_all_promotions(db: Database):
    cursor = db[PROMO_COLLECTION].find()
    return [format_promotion(doc) for doc in cursor]

def get_promotion(db: Database, promo_id: str):
    doc = db[PROMO_COLLECTION].find_one({"_id": ObjectId(promo_id)})
    return format_promotion(doc) if doc else None

def create_promotion(db: Database, data: dict):
    result = db[PROMO_COLLECTION].insert_one(data)
    return get_promotion(db, str(result.inserted_id))

def delete_promotion(db: Database, promo_id: str):
    db[PROMO_COLLECTION].delete_one({"_id": ObjectId(promo_id)})

def format_promotion(doc):
    return {
        "id": str(doc["_id"]),
        "name": doc["name"],
        "description": doc["description"],
        "discount": doc["discount"],
        "products": doc.get("products", [])
    }

def get_promotions_by_product_id(db: Database, product_id: int) -> list[dict]:
    cursor = db["promotions"].find({"products": product_id})
    return [format_promotion(doc) for doc in cursor]
