import abc
import asyncio
import json
from asyncio.log import logger
from json import JSONDecodeError

from pydantic import ValidationError
import aio_pika

from opendota_client.workers.exceptions import EmptyQueueException


class Worker(abc.ABC):
    _connect_attempts = 10
    _timeout = 10
    _prefetch_count = 1
    __received_message_model = None

    def __init__(self, broker: str):
        self.tasks_broker = broker
        self.channel = None
        self.slaves = RoundRobinQueue()

    async def start(self):
        for attempt in range(self._connect_attempts):
            try:
                self.connection = await aio_pika.connect_robust(url=self.tasks_broker)
                break
            except ConnectionError as error:
                if attempt == self._connect_attempts - 1:
                    raise error
                await asyncio.sleep(self._timeout)

        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=self._prefetch_count)
        queue = await self.channel.declare_queue("master", durable=True)
        await queue.consume(self._process_message)

    async def stop(self):
        await self.connection.close()

    async def _process_message(self, message: aio_pika.abc.AbstractIncomingMessage):
        async with message.process(ignore_processed=True):
            try:
                message_json = json.loads(message.body.decode())
            except (JSONDecodeError, TypeError):
                await message.reject()
            try:
                message_model = self.__received_message_model(**message_json)
            except ValidationError:
                logger.error(f"Переданные в задании данные не соответствуют установленному контракту: {message_json}")
                return
            logger.info(
                f"Message received: {message_model.dict()}"
            )
            await self.handle_message(message_model)

    @abc.abstractmethod
    async def handle_message(self, message):
        ...


class RoundRobinQueue:
    def __init__(self, entries=None):
        if entries is None:
            entries = list()
        self.container = entries
        self.pointer = 0

    def pop(self):
        if len(self.container) == 0:
            raise EmptyQueueException
        elif self.pointer == len(self.container)-1:
            self.pointer = 0
        else:
            self.pointer += 1
        return self.container[self.pointer]

    def add(self, entry):
        self.container.append(entry)
