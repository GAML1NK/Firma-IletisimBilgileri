from flask import Flask, request, jsonify, send_from_directory
import json
import os
from bs4 import BeautifulSoup
import requests
import re
import whois
import aiohttp
import asyncio
from concurrent.futures import ThreadPoolExecutor
from thefuzz import fuzz

app = Flask(__name__)

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY") # RapidAPI Key for SerpScraper API veri çekmek için kullanılmıştır.

# Asenkron HTTP POST isteği gönderir ve JSON yanıtını döner
async def fetch(session, url, headers, payload):
    async with session.post(url, headers=headers, data=payload) as response:
        return await response.json()

# SerpScraper API'ye istek gönderir ve sonuçları döner
async def get_search_results(query, engine, location="Istanbul,Turkey", limit=100):
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

# URL'den iletişim bilgilerini çıkarır ve döner
def extract_contact_info(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()

        phones, emails = check_text_blocks(text)
        valid_phones = list({phone for phone in phones if is_valid_phone_number(phone)})
        valid_emails = list({email for email in emails if is_valid_email(email)})

        return {"phones": valid_phones, "emails": valid_emails}
    except requests.RequestException as e:
        print("HTTP Hatası:", e)
        return {"phones": [], "emails": []}

# Metin içindeki telefon numaralarını ve e-posta adreslerini döner
def check_text_blocks(text):
    phone_pattern = re.compile(r'\+?\d[\d\-\(\) ]{7,}\d')
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

    phone_numbers = re.findall(phone_pattern, text)
    emails = re.findall(email_pattern, text)
    
    return phone_numbers, emails

# Telefon numarasının geçerli olup olmadığını kontrol eder
def is_valid_phone_number(number):
    phone_pattern = re.compile(r'\+?\d{1,4}?[-.\s]?(\(?\d{1,3}?\)?[-.\s]?)?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}')
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    return bool(phone_pattern.match(number)) and not bool(date_pattern.match(number))

# E-posta adresinin geçerli olup olmadığını kontrol eder
def is_valid_email(email):
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    return bool(email_pattern.match(email))

# WHOIS bilgilerini alır ve ülke bilgisini döner
def get_whois_info(domain):
    try:
        if domain.endswith(".tr"):
            return "Türkiye"
        whois_info = whois.whois(domain)
        return whois_info.country
    except Exception as e:
        print("WHOIS Hatası:", e)
        return "Bilinmiyor"

# İki metin arasında benzerlik oranında benzerlik olup olmadığını kontrol eder
def fuzzy_match(term, text, threshold=90):
    return fuzz.partial_ratio(term.lower(), text.lower()) >= threshold

# Arama sonuçlarını döner
@app.route('/ara', methods=['POST'])
async def ara():
    data = request.json
    firma_adi = data.get('firmaAdi')

    if not firma_adi: # Firma adı girilmediyse hata döner
        return jsonify({"error": "Firma adı gerekli"}), 400

    try:
        engines = ["google_search", "bing_search", "copilot_search"]
        queries = [firma_adi, f"{firma_adi} iletişim", f"{firma_adi} contact"]

        tasks = [] # Asenkron görevler listesi
        for engine in engines:
            for query in queries:
                tasks.append(get_search_results(query, engine))

        search_results = await asyncio.gather(*tasks)
        
        all_results = [] # Tüm sonuçlar listesi
        for result in search_results:
            if 'results' in result and result['results']:
                results_content = result['results'][0]['content']
                organic_results = results_content.get("results", {}).get("organic", [])
                for res in organic_results:
                    title = res.get("title", "")
                    snippet = res.get("snippet", "")
                    if fuzzy_match(firma_adi, title) or fuzzy_match(firma_adi, snippet):
                        all_results.append(res)

        final_results = [] # Sonuçlar listesi
        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(executor, extract_contact_info, result.get("url"))
                for result in all_results
            ]
            contact_infos = await asyncio.gather(*tasks)

        for result, contact_info in zip(all_results, contact_infos):# Sonuçlar ve iletişim bilgileri eşleştirilir
            if contact_info['phones'] or contact_info['emails']:
                website = result.get("url")
                domain = website.split("//")[-1].split("/")[0]
                country = get_whois_info(domain)
                result_data = {
                    "url": website,
                    "phones": contact_info['phones'],
                    "emails": contact_info['emails'],
                    "country": country
                }
                final_results.append(result_data)
        
        return jsonify(final_results)
        
    except Exception as e:# Hata durumunda hata döner
        return jsonify({"error": str(e)}), 500

# Ana sayfayı çalıştırır
@app.route('/')
def index():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
