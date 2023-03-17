import asyncio

import aiohttp
import pymongo

from opendota_client.client import get_matches


async def main():
    mongo = pymongo.MongoClient("localhost")
    database = mongo.get_database("hero_picker")
    collection = database.get_collection("matches")
    async with aiohttp.ClientSession() as session:
        await get_matches(session, collection)

if __name__ == "__main__":
    asyncio.run(main())
