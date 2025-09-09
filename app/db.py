from pymongo import MongoClient, ASCENDING, DESCENDING
from .settings import settings

_client = None
_db = None

def get_db():
    return _db

def init_db():
    global _client, _db
    _client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=3000)
    _db = _client[settings.mongo_db]

    # Minimal indexes
    _db["events"].create_index([("player_id", ASCENDING), ("ts", DESCENDING)])
    _db["events"].create_index([("game_id", ASCENDING), ("ts", DESCENDING)])
    _db["events"].create_index([("idempotent_key", ASCENDING)], unique=True, sparse=True)

    _db["stats"].create_index([("player_id", ASCENDING), ("game_id", ASCENDING)], unique=True)
    _db["stats"].create_index([("score", DESCENDING)])
    _db["player_achievements"].create_index([("player_id", ASCENDING)])
    _db["player_achievements"].create_index([("achievement_id", ASCENDING)])
