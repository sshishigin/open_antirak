from datetime import datetime
from typing import Dict

import aiohttp

from opendota_client.settings import WorkerSettings
from opendota_client.workers.models import SlaveMessage, MasterMessage, SlaveData, SetupMessage
from opendota_client.workers.base import Worker
from opendota_client.client import get_matches_list


class Master(Worker):
    async def decode(self, message_json):
        return SlaveMessage(**message_json)

    def __init__(self, broker: str, name="master"):
        super().__init__(broker)
        self.name = name
        self.min_match_id = None
        self.slaves: Dict[str, SlaveData] = {}

    async def handle_message(self, message: SlaveMessage):
        if message.type == "ready":
            await self.send_work(message.slave_id)
        elif message.type == "hello":
            await self.greet_new_slave(message.slave_id)

    async def send_work(self, slave_id):
        async with aiohttp.ClientSession() as session:
            matches = await get_matches_list(session, self.min_match_id)
            self.min_match_id = matches[-1]
            outgoing_message = MasterMessage(type="work", body=matches)
        await self.send_message(slave_id, outgoing_message)

    async def greet_new_slave(self, slave_id):
        if slave := self.slaves.get(slave_id):
            slave.status = "working"
            slave.last_active = datetime.now()
        else:
            self.slaves[slave_id] = SlaveData(
                status="working",
                last_task=None,
                last_active=datetime.now()
            )
        settings = WorkerSettings()
        message = MasterMessage(
            type="setup",
            body=SetupMessage(
                data_destination=settings.DATABASE,
                request_limit=50,
                limit_period=60
            )
        )
        await self.send_message(slave_id, message)
