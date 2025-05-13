from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client['forward_bot']
coll = db['user_settings']

def set_channel(user_id, channel_type, channel_id):
    coll.update_one(
        {"_id": user_id},
        {"$set": {channel_type: channel_id}},
        upsert=True
    )

def get_user_settings(user_id):
    return coll.find_one({"_id": user_id})

def set_active(user_id, status):
    coll.update_one({"_id": user_id}, {"$set": {"active": status}})

def get_all_active():
    return coll.find({"active": True})

async def is_admin(client, channel_id: str) -> bool:
    try:
        member = await client.get_chat_member(channel_id, "me")
        return member.status in ("administrator", "creator")
    except Exception as e:
        print(f"Admin check failed: {e}")
        return False
