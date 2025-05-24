import requests
import uuid
import os
from PIL import Image

API_KEY = "sk-26eac1353e1ec9ddde1a42ed195e191f"
IMAGE_PATH = "example.jpeg"
PROMPT = "Одинокий волк идет по пустынной дороге на закате"
DURATION = 5
QUALITY = "360p"
PROCESSED_IMAGE_PATH = "processed_image.jpg"

def generate_trace_id():
    return str(uuid.uuid4())

def get_balance(api_key):
    url = "https://app-api.pixverse.ai/openapi/v2/account/balance"
    headers = {
        "API-KEY": api_key,
        "Ai-trace-id": generate_trace_id()
    }
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        if data.get("ErrCode", 0) == 0:
            return data["Resp"]
        else:
            print("⚠️ Ошибка при получении баланса:", data)
    except Exception as e:
        print("❌ Ошибка при получении баланса:", str(e))
    return None

def preprocess_image(input_path, output_path=PROCESSED_IMAGE_PATH, max_size=4000):
    print("🛠️ Обрабатываем изображение перед загрузкой...")
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        img.thumbnail((max_size, max_size))
        img.save(output_path, "JPEG", quality=95)
    print(f"✅ Изображение сохранено как {output_path}")
    return output_path

def upload_image(api_key, image_path):
    url = "https://app-api.pixverse.ai/openapi/v2/image/upload"
    headers = {
        "API-KEY": api_key,
        "Ai-trace-id": generate_trace_id(),
    }
    with open(image_path, 'rb') as f:
        files = {'image': (os.path.basename(image_path), f, 'image/jpeg')}
        print("⬆️ Загружаем изображение...")
        response = requests.post(url, headers=headers, files=files)
        data = response.json()
        if response.status_code == 200 and data.get("Resp", {}).get("img_id"):
            print(f"✅ Изображение загружено. img_id: {data['Resp']['img_id']}")
            return data['Resp']['img_id']
        raise Exception(f"❌ Ошибка загрузки изображения: {data}")

def generate_video(api_key, img_id, prompt, duration=5, quality="360p"):
    url = "https://app-api.pixverse.ai/openapi/v2/video/img/generate"
    headers = {
        "API-KEY": api_key,
        "Ai-trace-id": generate_trace_id(),
        "Content-Type": "application/json"
    }
    data = {
        "duration": duration,
        "img_id": img_id,
        "model": "v3.5",
        "motion_mode": "normal",
        "negative_prompt": "",
        "prompt": prompt,
        "quality": quality,
        "seed": 0,
        "water_mark": False,
    }

    print("🎬 Запрос на генерацию видео...")
    response = requests.post(url, headers=headers, json=data)
    data = response.json()
    if response.status_code == 200:
        print("✅ Видео сгенерировано.")
        return data
    raise Exception(f"❌ Ошибка генерации видео: {data}")

if __name__ == "__main__":
    try:
        balance = get_balance(API_KEY)
        if not balance:
            print("❌ Не удалось получить баланс.")
            exit()

        total_credits = balance.get("credit_package", 0) + balance.get("credit_monthly", 0)
        print(f"💰 Баланс: {total_credits}")
        if total_credits <= 0:
            print("❌ Недостаточно кредитов.")
            exit()

        processed_path = preprocess_image(IMAGE_PATH)
        img_id = upload_image(API_KEY, processed_path)
        response = generate_video(API_KEY, img_id, PROMPT, DURATION, QUALITY)
        print("📦 Ответ от сервера:", response)
    except Exception as e:
        print("❌ Произошла ошибка:", str(e))
