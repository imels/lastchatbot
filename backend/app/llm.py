import google.generativeai as genai
import os
from dotenv import load_dotenv

# .env'den API anahtarını yükle
load_dotenv()
genai.api_key = os.getenv("GOOGLE_API_KEY")
if not genai.api_key:
    raise ValueError("❌ GOOGLE_API_KEY bulunamadı! Lütfen .env dosyasını kontrol edin.")

def chat_completion(messages):
    """
    Google Generative AI ile sohbet cevapları oluşturur.
    messages: [{"role": "user"|"assistant", "content": "..."}]
    """
    try:
        # Mesajlardaki "assistant" rolünü Gemini'nin "model" rolüne dönüştürür.
        gemini_messages = [
            {"role": "model" if m["role"] == "assistant" else m["role"], "parts": [m["content"]]}
            for m in messages
        ]
        
        # Ücretsiz ve hızlı olan gemini-1.5-flash modelini kullanır.
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Modelden cevap alır.
        response = model.generate_content(gemini_messages)
        
        # Sadece metin içeriğini döndürür.
        return response.text
        
    except Exception as e:
        print(f"❌ Gemini API Hatası: {e}")
        return "Üzgünüm, bir hata oluştu ve cevap veremedim."