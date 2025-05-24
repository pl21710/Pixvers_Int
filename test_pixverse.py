from services.pixverse import PixVerseClient
import time

# 🔐 Настройки
API_KEY = "sk-26eac1353e1ec9ddde1a42ed195e191f"
APP_BUNDLE_ID = "com.test.app"
APPHUD_USER_ID = "test_user_123"

# 📦 Клиент
client = PixVerseClient(API_KEY, APP_BUNDLE_ID, APPHUD_USER_ID)

# 💳 Проверка баланса
balance = client.get_credit_balance()
if not balance:
    print("❌ Не удалось получить баланс.")
    exit()

total_credits = balance.get("credit_package", 0) + balance.get("credit_monthly", 0)
print(f"💰 Текущий баланс: {total_credits} (Покупные: {balance.get('credit_package', 0)}, Подписка: {balance.get('credit_monthly', 0)})")

if total_credits <= 0:
    print("❌ Недостаточно кредитов для генерации видео.")
    exit()

# 📜 Промпт
prompt_text = "A lonely wolf walking down a desert road at sunset"
print("🔄 Генерация видео из текста...")

# 🎬 Запрос
response = client.text_to_video(prompt=prompt_text, duration=5, quality="360p")
print("📨 Ответ сервера:", response)

if response.get("ErrCode") != 0:
    print(f"❌ Ошибка генерации: [{response.get('ErrCode')}] {response.get('ErrMsg')}")
    exit()

video_id = response.get("Resp", {}).get("video_id")
if not video_id:
    print("❌ video_id не получен.")
    exit()

print(f"🆔 Видео запрошено. ID задачи: {video_id}")
print("⏳ Ожидание завершения...")

# 🔄 Опрос
for i in range(10):
    status = client.get_video_status(video_id)
    print(f"[{i+1}/10] Статус:", status)

    if status.get("status") == "done":
        print("✅ Готово! Видео:", status.get("video_url"))
        break
    elif status.get("status") == "error":
        print("❌ Ошибка генерации.")
        break
    time.sleep(60)
