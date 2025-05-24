from services.pixverse import PixVerseClient
import time
from services.Telegram import send_telegram_alert

# Настройки
API_KEY = "sk-26eac1353e1ec9ddde1a42ed195e191f"
APP_BUNDLE_ID = "com.test.app"
APPHUD_USER_ID = "test_user_123"

client = PixVerseClient(API_KEY, APP_BUNDLE_ID, APPHUD_USER_ID)

# Проверка баланса
balance = client.get_credit_balance()
if not balance:
    print("❌ Не удалось получить баланс.")
    send_telegram_alert("❌ Не удалось получить баланс PixVerse.")
    exit()

total_credits = balance.get("credit_package", 0) + balance.get("credit_monthly", 0)
if total_credits <= 0:
    print("❌ Недостаточно кредитов.")
    send_telegram_alert("❌ Недостаточно кредитов для генерации видео.")
    exit()

prompt_text = "A lonely wolf walking down a desert road at sunset"
print("🔄 Генерация видео из текста...")
send_telegram_alert(f"📤 Запрос на генерацию видео из текста:\n📜 Промпт: {prompt_text}")

response = client.text_to_video(prompt=prompt_text, duration=5, quality="360p")
print("📨 Ответ сервера:", response)

if response.get("ErrCode") != 0:
    msg = f"❌ Ошибка генерации видео из текста:\n[{response.get('ErrCode')}] {response.get('ErrMsg')}"
    print(msg)
    send_telegram_alert(msg)
    exit()

video_id = response.get("Resp", {}).get("video_id")
if not video_id:
    print("❌ video_id не получен.")
    send_telegram_alert("❌ Не получен video_id после генерации.")
    exit()

print(f"🆔 Видео запрошено. ID задачи: {video_id}")
send_telegram_alert(f"✅ Видео из текста запрошено.\n🆔 ID задачи: {video_id}")

# 🔄 Опрос
for i in range(10):
    print(f"⏳ Проверка статуса... попытка {i+1}/10")
    status = client.get_video_status(video_id)
    print(f"[{i+1}/10] Статус:", status)

    video_status = status.get("status")
    if video_status == "done":
        video_url = status.get("video_url")
        print("✅ Готово! Видео:", video_url)
        send_telegram_alert(f"✅ Видео из текста готово!\n🎬 Ссылка: {video_url}")
        break
    elif video_status == "error":
        print("❌ Ошибка генерации.")
        send_telegram_alert("❌ Ошибка генерации видео из текста.")
        break

    time.sleep(60)
else:
    send_telegram_alert("⌛ Видео из текста не готово даже после 10 попыток.")
