from beanie import init_beanie
import config
from motor.motor_asyncio import AsyncIOMotorClient

from models.user import User
from models.data import Grup

async def init():
    client = AsyncIOMotorClient(config.MONGO_DB_URL)
    await init_beanie(client.topic_bot, document_models=[User, Grup])
    return True