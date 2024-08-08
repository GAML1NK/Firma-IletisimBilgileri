# Description: This file is used to extract contact information from the given URL.
# Açıklayıcı Not: Bu dosya, verilen URL'den iletişim bilgilerini çıkarmak için kullanılır.
from bs4 import BeautifulSoup
import requests
import re

from helper import is_valid_email, is_valid_phone_number

def extract_contact_info(url):
    print("1Bitiiiiiiiiiiiiiiiiiiiiiiiiiii")
    if url.find("instagram") != -1:   
        return {"phones": [], "emails": []} 
    try:
        response = requests.get(url)
        print("2Bitiiiiiiiiiiiiiiiiiiiiiiiiiii")
        response.raise_for_status()
        
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text()
            #print(html_content)
            print("3Bitiiiiiiiiiiiiiiiiiiiiiiiiiii")

            phones, emails = check_text_blocks(text)
            valid_phones = list({phone for phone in phones if is_valid_phone_number(phone)})
            valid_emails = list({email for email in emails if is_valid_email(email)})

            return {"phones": valid_phones, "emails": valid_emails}
        else:
            print(f"HTTP isteği başarısız oldu. Durum kodu: {response.status_code}")
            return {"phones": [], "emails": []}
    except requests.RequestException as e:
        print("4Bitiiiiiiiiiiiiiiiiiiiiiiiiiii")
        print("HTTP Hatası:", e)
        return {"phones": [], "emails": []}

def check_text_blocks(text):
    print("5Bitiiiiiiiiiiiiiiiiiiiiiiiiiii")
    phone_pattern = re.compile(r'\+?\d[\d\-\(\) ]{7,}\d')
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

    phone_numbers = re.findall(phone_pattern, text)
    emails = re.findall(email_pattern, text)
    print("6Bitiiiiiiiiiiiiiiiiiiiiiiiiiii")
    
    return phone_numbers, emails