from uuid import uuid4

import aiohttp
import pymongo.collection

from opendota_client.client import get_match, save_match
from opendota_client.workers.models import MasterMessage, SlaveMessage
from opendota_client.workers.base import Worker


class Slave(Worker):

    async def decode(self, message_json):
        return MasterMessage(**message_json)

    def __init__(self, broker: str):
        super().__init__(broker)
        self._collection: pymongo.collection.Collection | None = None
        self.name = "slave_" + str(uuid4())

    async def on_start(self):
        await self.greet_the_master()

    async def handle_message(self, message: MasterMessage):
        if message.type == "work":
            async with aiohttp.ClientSession() as session:
                for match_id in message.body:
                    match = await get_match(session, match_id)
                    save_match(self._collection, match)
            await self.send_ready_message()
        elif message.type == "setup":
            await self.setup(data_destination=message.body["data_destination"])

    async def setup(self, data_destination):
        mongo = pymongo.MongoClient(data_destination)
        database = mongo.get_database("hero_picker")
        self._collection = database.get_collection("matches")
        await self.send_ready_message()

    async def send_ready_message(self):
        await self.send_message("master", SlaveMessage(type="ready", slave_id=self.name))

    async def greet_the_master(self):
        await self.send_message("master", SlaveMessage(type="hello", slave_id=self.name))
