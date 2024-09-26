from flask import Flask,  request, jsonify, send_from_directory
import os
from fetch import get_search_results
from helper import fuzzy_match
from url import extract_contact_info_with_selenium
import whois
import asyncio
from concurrent.futures import ThreadPoolExecutor




app = Flask(__name__)



@app.route('/ara', methods=['POST'])
async def ara():
    data = request.json
    firma_adi = data.get('firmaAdi')

    if not firma_adi:
        return jsonify({"error": "Firma adı gerekli"}), 400

    try:
        engines = ["google_search", "bing_search","yandex_search"]
        queries = [firma_adi, f"{firma_adi} iletişim", f"{firma_adi} contact", f"{firma_adi} contect-us", f"{firma_adi} bize-ulasin"]
            
        tasks = []
        for engine in engines:
            for query in queries:
                tasks.append(get_search_results(query, engine))

        search_results = await asyncio.gather(*tasks)
        
        all_results = []
        for result in search_results:
            if 'results' in result and result['results']:
                results_content = result['results'][0]['content']
                organic_results = results_content.get("results", {}).get("organic", [])
                for res in organic_results:
                    title = res.get("title", "")
                    snippet = res.get("snippet", "")
                    if fuzzy_match(firma_adi, title) or fuzzy_match(firma_adi, snippet):
                        all_results.append(res)

    

        final_results = []
        with ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(executor, extract_contact_info_with_selenium, result.get("url"))
                for result in all_results
            ]
            contact_infos = await asyncio.gather(*tasks)

        for result, contact_info in zip(all_results, contact_infos):
            if contact_info['phones'] or contact_info['emails']:
                website = result.get("url")
                domain = website.split("//")[-1].split("/")[0]
                country = whois.get_whois_info(domain)
                result_data = {
                    "url": website,
                    "phones": contact_info['phones'],
                    "emails": contact_info['emails'],
                    "social_media": contact_info['social_media'],
                    "country": country
                }
                final_results.append(result_data)
        
        return jsonify(final_results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
