import google.generativeai as genai
import os

def analyze_transcript(transcript):
    """
    Analyze video transcript using Google Gemini API to extract locations and landmarks.
    """
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')

    prompt = f"""
    Aşağıdaki metinden turistik yerleri, tarihi mekanları ve önemli lokasyonları çıkar.
    Sadece kesin olarak yer ismi olan lokasyonları liste halinde döndür.
    Örnek kabul edilebilir yerler:
    - Pantheon
    - Trevi Çeşmesi
    - Colosseum
    - Piazza Navona

    Örnek kabul edilemez yerler:
    - bu sokak
    - şu cadde
    - merkez
    - bahçe

    Metin:
    {transcript}
    """

    response = model.generate_content(prompt)
    locations = []

    if response.text:
        # Her satırı işle ve '-' ile başlayanları al
        for line in response.text.split('\n'):
            if line.strip().startswith('-'):
                location = line.strip()[1:].strip()  # '-' işaretini kaldır ve boşlukları temizle
                if location:
                    locations.append(location)

    return locations

def analyze_video_title(title):
    """
    Analyze video title to determine main location context.
    """
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')

    prompt = f"""
    Bu video başlığından veya metnin ilk cümlelerinden ana şehir veya bölgeyi kesin olarak tespit et:
    {title}

    Sadece şehir/bölge adını döndür (örnek: Roma, Paris, Londra).
    Eğer kesin değilsen boş döndür.
    """

    response = model.generate_content(prompt)
    return response.text.strip() if response.text else None