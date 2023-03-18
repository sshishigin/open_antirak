from pydantic import BaseSettings


class WorkerSettings(BaseSettings):
    BROKER: str = "amqp://localhost"
    DATABASE: str = "localhost"
