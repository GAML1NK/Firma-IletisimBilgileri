# Description: This file is used to extract contact information from the given URL.
# Açıklayıcı Not: Bu dosya, verilen URL'den iletişim bilgilerini çıkarmak için kullanılır.
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

from helper import check_social_media_links, check_text_blocks, is_valid_email, is_valid_phone_number

def extract_contact_info_with_selenium(url):
    start_time = time.time()

    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Tarayıcıyı arka planda çalıştırır.
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Headless modda çalıştır
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        print("selenium kalktı")

        driver.get(url)
        driver.implicitly_wait(3)
        print("url okundu")
        html_content = driver.page_source
        # print("html_content okundu", html_content)
        end_time = time.time()
        elapsed_time = end_time - start_time
        # print("Elapsed time:", elapsed_time)

        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()

        phones, emails = check_text_blocks(text)
        valid_phones = list({phone for phone in phones if is_valid_phone_number(phone)})
        valid_emails = list({email for email in emails if is_valid_email(email)})

    #    html_content1 = '''
    #        <a href="https://www.facebook.com/example">Facebook</a>
    #        <a href="https://twitter.com/example">Twitter</a>
    #        <a href="https://www.instagram.com/example">Instagram</a>
    #        <a href="https://www.linkedin.com/in/example">LinkedIn</a>
    #        <a href="https://www.youtube.com/user/example">YouTube</a>
    #        <a href="https://www.pinterest.com/example">Pinterest</a>
    #    '''
        social_media_links = check_social_media_links(html_content)
        # print("valid_phones", valid_phones)
        # print("valid_emails", valid_emails)
        # print("social_media_links", social_media_links)

        driver.quit()

        return {"phones": valid_phones, "emails": valid_emails , "social_media": social_media_links}

    except Exception as e:
        print("4Bitiiiiiiiiiiiiiiiiiiiiiiiiiii")
        print("Hata:", e)
        return {"phones": [], "emails": []}
