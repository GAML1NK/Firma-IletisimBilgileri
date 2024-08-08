# Açıklama: Bu dosya, verilen URL'den iletişim bilgilerini çıkarmak için kullanılır.


import whois







def get_whois_info(domain):
    print("9Bitiiiiiiiiiiiiiiiiiiiiiiiiiii")
    try:
        if domain.endswith(".tr"):
            return "Türkiye"
        whois_info = whois.whois(domain)
        return whois_info.country
    except Exception as e:
        print("WHOIS Hatası:", e)
        return "Bilinmiyor"
