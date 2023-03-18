import pydantic


class SlaveMessageModel(pydantic.BaseModel):
    slave_id: str
    type: str


class MasterMessageModel(pydantic.BaseModel):
    type: str
    body: dict | list