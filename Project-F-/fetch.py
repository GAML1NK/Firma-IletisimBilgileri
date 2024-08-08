import json
import aiohttp

RAPIDAPI_KEY = "9b3516ecbbmsh64ff8f30a56080ep1788dbjsn142564369fd8"

async def fetch(session, url, headers, payload):
    async with session.post(url, headers=headers, data=payload) as response:
        return await response.json()

async def get_search_results(query, engine, location="Istanbul,Turkey", limit=12):
    url = "https://serp-scraper-api.p.rapidapi.com/queries"
    payload = json.dumps({
        "source": engine,
        "query": query,
        "geo_location": location,
        "parse": True,
        "limit": limit
    })
    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': "serp-scraper-api.p.rapidapi.com",
        'Content-Type': "application/json"
    }
    async with aiohttp.ClientSession() as session:
        response = await fetch(session, url, headers, payload)
        return response