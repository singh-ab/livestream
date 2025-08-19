import os
from motor.motor_asyncio import AsyncIOMotorClient

_MONGO_CLIENT = None
_DB = None

async def get_db():
    global _MONGO_CLIENT, _DB
    if _DB is None:
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB", "livestream")
        _MONGO_CLIENT = AsyncIOMotorClient(uri)
        _DB = _MONGO_CLIENT[db_name]
    return _DB


async def get_overlays_collection():
    db = await get_db()
    return db.get_collection("overlays")
