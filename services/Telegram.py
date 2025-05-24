import requests

TELEGRAM_BOT_TOKEN = "7940124863:AAHRSsYon301ilHjJuNr8XCSWJLiU-qZDvg"
TELEGRAM_CHAT_ID = "914923628"  # можно узнать, написав боту и вызвав getUpdates

def send_telegram_alert(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Ошибка отправки в Telegram: {e}")
if __name__ == "__main__":
    send_telegram_alert("🚨 Тестовое сообщение из Telegram-бота! Всё работает ✅")