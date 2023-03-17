from opendota_client.workers.models import MasterMessageModel
from opendota_client.workers.base import Worker


class Slave(Worker):
    __received_message_model = MasterMessageModel

    def handle_message(self, message):
        ...