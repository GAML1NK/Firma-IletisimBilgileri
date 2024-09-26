# Description: This file contains helper functions that are used in the app.py file.
# Açıklayıcı Not: Bu dosya, app.py dosyasında kullanılan yardımcı işlevleri içerir.
from flask import Flask, request, jsonify, send_from_directory
import re
from thefuzz import fuzz



def check_text_blocks(text):
    phone_pattern = re.compile(r'\+?\d[\d\-\(\) ]{7,}\d')
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

    phone_numbers = re.findall(phone_pattern, text)
    emails = re.findall(email_pattern, text)
    
    return phone_numbers, emails

def is_valid_phone_number(number):
    phone_pattern = re.compile(r'\+?\d{1,4}?[-.\s]?(\(?\d{1,3}?\)?[-.\s]?)?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}')
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    return bool(phone_pattern.match(number)) and not bool(date_pattern.match(number))

def is_valid_email(email):
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    return bool(email_pattern.match(email))
def fuzzy_match(term, text, threshold=90):
    return fuzz.partial_ratio(term.lower(), text.lower()) >= threshold

def check_social_media_links(content):
    # Sosyal medya linklerini yakalayacak regex
    social_media_regex = r'(https?:\/\/(?:www\.)?(facebook|twitter|instagram|linkedin|youtube|pinterest)\.com\/[^\s"\']*)'

    # Tüm URL ve platform eşleşmelerini bul
    matches = re.findall(social_media_regex, content)
    
    # Platform bazlı URL'leri saklamak için bir sözlük oluştur
    links = {
        'facebook': [],
        'twitter': [],
        'instagram': [],
        'linkedin': [],
        'youtube': [],
        'pinterest': []
    }
    
    # Eşleşmeleri dolaşarak uygun platforma göre URL'leri sınıflandır
    for url, platform in matches:
        if platform in links:
            links[platform].append(url)
    
    # Elde edilen platform ve URL eşleşmelerini yazdır
    print("Eşleşmeler:", matches)
    print("Platform bazlı linkler:", links)
    
    # Links sözlüğünü geri döndür
    return links
