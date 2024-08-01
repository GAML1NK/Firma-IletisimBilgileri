from flask import Flask, request, jsonify, send_from_directory
import http.client
import json
import os
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)

RAPIDAPI_KEY = "***" # Burada rapidApi üzerinden -Serp Scraper API- için oluşturduğunuz key'i girmeniz gerekmektedir. -ücretsidir-
# Google arama sonuçları alınıyor.
def get_google_search_results(query, location):
    conn = http.client.HTTPSConnection("serp-scraper-api.p.rapidapi.com")
    payload = json.dumps({
        "source": "google_search",
        "query": query,
        "geo_location": location,
        "parse": True,
        "limit": 1  # İlk sonuç için limit 1
    })
    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': "serp-scraper-api.p.rapidapi.com",
        'Content-Type': "application/json"
    }
    conn.request("POST", "/queries", payload, headers)
    res = conn.getresponse()
    data = res.read()
    response_json = json.loads(data.decode("utf-8"))
    return response_json
# Url'den telefon numarası ve email bilgileri çekiliyor.
def extract_contact_info(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()

        phones, emails = check_text_blocks(text)
        
        # Aynı numradan başka var mı diye kontrol ediyoruz ve telefon numarası olup olmadığını kontrol ediyoruz.
        valid_phones = list({phone for phone in phones if is_valid_phone_number(phone)})
        valid_emails = list({email for email in emails if is_valid_email(email)})
        
        return {"phones": valid_phones, "emails": valid_emails}
    except requests.RequestException as e:
        print("HTTP Hatası:", e)
        return {"phones": [], "emails": []}

def check_text_blocks(text, block_size=1000):# 1000 karakterlik bloklar halinde kontrol ediyoruz.
    phone_pattern = re.compile(r'\+?\d[\d\-\(\) ]{7,}\d')# Telefon numarası için regex
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')# Email için regex

    phone_numbers = set()
    emails = set()
    
    phones = re.findall(phone_pattern, text)
    emails_found = re.findall(email_pattern, text)
        
    phone_numbers.update(phones)
    emails.update(emails_found)
    
    return list(phone_numbers), list(emails)
# Telefon numarası ve email kontrolü yapılıyor.
def is_valid_phone_number(number):
    phone_pattern = re.compile(r'^\+?\d[\d\-\(\) ]{7,}\d$')
    return bool(phone_pattern.match(number))

def is_valid_email(email):
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    return bool(email_pattern.match(email))
# Post request ile gelen firma adına göre arama yapılıyor.
@app.route('/ara', methods=['POST'])
def ara():
    data = request.json
    firma_adi = data.get('firmaAdi')
    
    if not firma_adi:
        return jsonify({"error": "Firma adı gerekli"}), 400

    try:
        results = get_google_search_results(firma_adi, "Istanbul,Turkey")
        
        if 'results' not in results or not results['results']:
            return jsonify({"error": "Arama sonucu bulunamadı"}), 404
        
        results_content = results['results'][0]['content']
        organic_results = results_content.get("results", {}).get("organic", [])
        
        if not organic_results:
            return jsonify({"error": "Arama sonucu bulunamadı"}), 404
        
        first_result = organic_results[0]
        website = first_result.get("url")
        
        contact_info = extract_contact_info(website)
        
        return jsonify(contact_info)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# index.html dosyası gönderiliyor.
@app.route('/')
def index():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'index.html')
# Uygulama çalıştırılıyor.
if __name__ == '__main__':
    app.run(debug=True)
