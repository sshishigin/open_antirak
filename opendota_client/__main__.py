import asyncio
import sys

import pymongo

from opendota_client.settings import WorkerSettings
from opendota_client.workers import Master, Slave


async def main():
    args = sys.argv
    settings = WorkerSettings()
    if len(args) == 1:
        print("master or slave?")
        sys.exit(1)
    worker_type = args[1]
    if worker_type == "slave":
        mongo = pymongo.MongoClient(settings.DATABASE)
        database = mongo.get_database("hero_picker")
        collection = database.get_collection("matches")
        worker = Slave(settings.BROKER, collection)
    elif worker_type == "master":
        worker = Master(settings.BROKER)
    else:
        print("Unknown worker type, exit")
        sys.exit(1)

    await worker.start()
    return worker


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    worker = loop.run_until_complete(main())
    asyncio.set_event_loop(loop)
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(worker.stop())
