import aiohttp
import aio_pika

from opendota_client.workers.models import SlaveMessageModel, MasterMessageModel
from opendota_client.workers.base import Worker
from opendota_client.client import get_matches_list


class Master(Worker):
    async def decode(self, message_json):
        return SlaveMessageModel(**message_json)

    def __init__(self, broker: str, name="master"):
        super().__init__(broker)
        self.name = name
        self.min_match_id = None

    async def handle_message(self, message: SlaveMessageModel):
        if message.type == "ready":
            async with aiohttp.ClientSession() as session:
                matches = await get_matches_list(session, self.min_match_id)
                self.min_match_id = matches[-1]
                outgoing_message = MasterMessageModel(type="work", body=matches)
            print(f"sending work message to {message.slave_id}")
            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=outgoing_message.json().encode()
                ),
                routing_key=message.slave_id
            )
            print("sent successfuly")
