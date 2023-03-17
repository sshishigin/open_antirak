from opendota_client.workers.models import SlaveMessageModel
from opendota_client.workers.base import Worker


class Master(Worker):
    __received_message_model = SlaveMessageModel

    def handle_message(self, message):
        ...