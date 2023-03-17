from opendota_client.ratelimiter import rate_limit

import aiohttp

import pymongo



@rate_limit
async def get_matches_list(session: aiohttp.ClientSession, lower_than=None):
    url = f"https://api.opendota.com/api/parsedMatches"
    async with session.get(url, params={"less_than_match_id": lower_than} if lower_than else None) as resp:
        matches = await resp.json()
    for match_id in [entry["match_id"] for entry in matches]:
        yield match_id


@rate_limit
async def get_match(session: aiohttp.ClientSession, match_id):
    url = "https://api.opendota.com/api/matches/" + str(match_id)
    async with session.get(url) as resp:
        match = await resp.json()
    return match


def save_match(collection: pymongo.collection.Collection, match: dict):
    collection.insert_one(match)


async def get_matches(session, collection):
    min_match_id = None
    while True:
        async for match_id in get_matches_list(session, min_match_id):
            if not min_match_id:
                min_match_id = match_id
            else:
                min_match_id = min((min_match_id, match_id))
            match = await get_match(session, match_id)
            save_match(collection, match)
