import requests

BOT_TOKEN = "7940124863:AAHRSsYon301ilHjJuNr8XCSWJLiU-qZDvg"
CHAT_ID = "914923628"


def send_telegram_alert(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        print("📤 Пытаемся отправить сообщение в Telegram...")
        print("📨 Данные:", data)
        response = requests.post(url, data=data)
        print("🔁 Ответ от Telegram:", response.status_code, response.text)
        if not response.ok:
            print("⚠️ Ошибка Telegram:", response.status_code, response.text)
    except Exception as e:
        print("❌ Telegram exception:", str(e))