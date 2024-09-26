from flask import Flask, request, jsonify, send_from_directory
import json
import aiohttp


app = Flask(__name__)

RAPIDAPI_KEY = "Buradaki kodu Serp RapidAPI'den alabilirsiniz."

async def fetch(session, url, headers, payload):
    async with session.post(url, headers=headers, data=payload) as response:
        return await response.json()

async def get_search_results(query, engine, location="Istanbul,Turkey", limit=1):
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

