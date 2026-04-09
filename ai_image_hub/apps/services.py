import requests
import os
from django.core.files.base import ContentFile
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

load_dotenv()
API_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
# Model Stable Diffusion XL hoặc Flux (đang rất hot năm 2026)
# Lưu ý: Hugging Face đã đổi đường dẫn API sang router.huggingface.co 
API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
headers = {"Authorization": f"Bearer {API_TOKEN}"}
def generate_ai_image(prompt):
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        
        if response.status_code == 200:
            # Trả về ContentFile để Django ImageField có thể lưu trực tiếp
            return ContentFile(response.content, name=f"temp_{os.urandom(4).hex()}.png")
        else:
            print(f"Lỗi API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Lỗi hệ thống: {e}")
        return None

def check_api_health():
    url = "https://huggingface.co/api/whoami-v2"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return True, "API (Token) đang hoạt động tốt!"
        elif response.status_code == 401:
            return False, "Token Hugging Face không hợp lệ hoặc đã hết hạn."
        else:
            return False, f"Lỗi không xác định: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Lỗi kết nối mạng: {e}"
def refine_prompt(vietnamese_prompt):
    """
    Dịch và làm đẹp prompt trước khi gửi cho AI tạo ảnh
    """
    try:
        # Dịch sang tiếng Anh
        english_prompt = GoogleTranslator(source='auto', target='en').translate(vietnamese_prompt)
        
        # Thêm một chút "gia vị" để ảnh đẹp hơn (Prompt Engineering)
        final_prompt = f"{english_prompt}, high resolution, 8k, detailed masterpiece"
        return final_prompt
    except:
        return vietnamese_prompt # Nếu lỗi thì dùng bản gốc