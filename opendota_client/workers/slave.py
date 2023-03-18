from datetime import datetime
from uuid import uuid4

import aio_pika
import aiohttp
import pymongo.collection

from opendota_client.client import get_match, save_match
from opendota_client.workers.models import MasterMessageModel, SlaveMessageModel
from opendota_client.workers.base import Worker


class Slave(Worker):

    async def decode(self, message_json):
        return MasterMessageModel(**message_json)

    def __init__(self, broker: str, collection: pymongo.collection.Collection):
        super().__init__(broker)
        self._collection = collection
        self.name = "slave_" + str(uuid4())

    async def on_start(self):
        await self.send_ready_message()

    async def handle_message(self, message: MasterMessageModel):
        if message.type == "work":
            async with aiohttp.ClientSession() as session:
                for match_id in message.body:
                    match = await get_match(session, match_id)
                    print(f"{datetime.now()} +1")
                    save_match(self._collection, match)
            await self.send_ready_message()

    async def send_ready_message(self):
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=SlaveMessageModel(type="ready", slave_id=self.name).json().encode()
            ),
            routing_key="master"
        )
