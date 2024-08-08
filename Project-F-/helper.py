# Description: This file contains helper functions that are used in the app.py file.
# Açıklayıcı Not: Bu dosya, app.py dosyasında kullanılan yardımcı işlevleri içerir.
import re
from thefuzz import fuzz




def is_valid_phone_number(number):
    print("7Bitiiiiiiiiiiiiiiiiiiiiiiiiiii")
    phone_pattern = re.compile(r'\+?\d{1,4}?[-.\s]?(\(?\d{1,3}?\)?[-.\s]?)?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}')
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    return bool(phone_pattern.match(number)) and not bool(date_pattern.match(number))

def is_valid_email(email):
    print("8Bitiiiiiiiiiiiiiiiiiiiiiiiiiii")
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    return bool(email_pattern.match(email))



def fuzzy_match(term, text, threshold=90):
    print("10Bitiiiiiiiiiiiiiiiiiiiiiiiiiii")
    return fuzz.partial_ratio(term.lower(), text.lower()) >= threshold