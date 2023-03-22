from datetime import datetime

import pydantic


class SlaveMessage(pydantic.BaseModel):
    slave_id: str
    type: str


class SetupMessage(pydantic.BaseModel):  # Сообщение которое клиент получает при регистрации у Мастера
    data_destination: str
    request_limit: int
    limit_period: int  # Период в секундах на который распространяется лимит


class MasterMessage(pydantic.BaseModel):
    type: str
    body: dict | list | SetupMessage


class SlaveTask(pydantic.BaseModel):
    _id: str
    status: str
    body: dict | list


class SlaveData(pydantic.BaseModel):
    status: str
    last_task: SlaveTask | None
    last_active: datetime
