import requests
import uuid
import os
import time
from PIL import Image
from Telegram import send_telegram_alert

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
    response = requests.get(url, headers=headers)
    data = response.json()
    if data.get("ErrCode") == 0:
        return data["Resp"]
    print("⚠️ Ошибка при получении баланса:", data)
    send_telegram_alert("❌ Ошибка при получении баланса PixVerse.")
    return None

def preprocess_image(input_path, output_path=PROCESSED_IMAGE_PATH, max_size=4000):
    print("🛠️ Обрабатываем изображение...")
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        img.thumbnail((max_size, max_size))
        img.save(output_path, "JPEG", quality=95)
    print(f"✅ Сохранено как {output_path}")
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
            print(f"✅ Загружено. img_id: {data['Resp']['img_id']}")
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

    print("🎬 Запрос генерации видео...")
    response = requests.post(url, headers=headers, json=data)
    data = response.json()
    if response.status_code == 200 and data.get("ErrCode") == 0:
        return data
    raise Exception(f"❌ Ошибка генерации видео: {data}")

def get_video_status(video_id):
    url = f"https://app-api.pixverse.ai/openapi/v2/video/query?video_id={video_id}"
    headers = {
        "API-KEY": API_KEY,
        "Ai-trace-id": generate_trace_id()
    }
    response = requests.get(url, headers=headers)
    return response.json().get("Resp", {})

if __name__ == "__main__":
    try:
        balance = get_balance(API_KEY)
        if not balance:
            exit()

        total_credits = balance.get("credit_package", 0) + balance.get("credit_monthly", 0)
        print(f"💰 Баланс: {total_credits}")
        if total_credits <= 0:
            send_telegram_alert("❌ Недостаточно кредитов для генерации видео.")
            exit()

        processed_path = preprocess_image(IMAGE_PATH)
        img_id = upload_image(API_KEY, processed_path)
        send_telegram_alert(f"📤 Генерация видео из изображения запущена.\n🖼️ img_id: {img_id}\n📜 Промпт: {PROMPT}")

        response = generate_video(API_KEY, img_id, PROMPT, DURATION, QUALITY)
        video_id = response["Resp"].get("video_id")

        if not video_id:
            send_telegram_alert("❌ Не получен video_id после генерации из изображения.")
            exit()

        send_telegram_alert(f"🆔 Видео запрошено. ID: {video_id}\n⏳ Ожидаем результат...")

        for i in range(10):
            print(f"⏳ Проверка статуса ({i+1}/10)...")
            status = get_video_status(video_id)
            print(f"Статус: {status.get('status')}")

            if status.get("status") == "done":
                video_url = status.get("video_url")
                print("✅ Готово:", video_url)
                send_telegram_alert(f"✅ Видео из изображения готово!\n📽️ Ссылка: {video_url}")
                break
            elif status.get("status") == "error":
                print("❌ Ошибка генерации.")
                send_telegram_alert("❌ Ошибка генерации видео из изображения.")
                break
            time.sleep(60)
        else:
            send_telegram_alert("⌛ Видео из изображения не готово даже после 10 попыток.")

    except Exception as e:
        print("❌ Произошла ошибка:", str(e))
        send_telegram_alert(f"❌ Ошибка при генерации видео из изображения:\n{str(e)}")
