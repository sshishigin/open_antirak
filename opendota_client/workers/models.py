import pydantic


class SlaveMessageModel(pydantic.BaseModel):
    slave_id: str
    message_type: str


class MasterMessageModel(pydantic.BaseModel):
    message_type: str
    body: dict
