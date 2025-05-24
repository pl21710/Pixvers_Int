from fastapi import APIRouter, UploadFile, File, Form
from services.pixverse import PixVerseClient
from PIL import Image
import tempfile
import os

router = APIRouter()

client = PixVerseClient(
    api_key="sk-26eac1353e1ec9ddde1a42ed195e191f", 
    app_bundle_id="com.example.app",
    apphud_user_id="example_user_id"
)

def preprocess_image(input_path, output_path="processed.jpg"):
    """
    Подгоняет изображение под допустимые размеры PixVerse (1024x576).
    Автоматически конвертирует в JPEG и RGB.
    """
    with Image.open(input_path) as img:
        img = img.convert("RGB")
        img = img.resize((1024, 576)) 
        img.save(output_path, "JPEG", quality=95)
    return output_path

@router.post("/generate-image2video")
async def generate_image2video(
    image: UploadFile = File(...),
    prompt: str = Form(...)
):
    print("🚀 Запрос получен")

    ext = os.path.splitext(image.filename)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(await image.read())
        temp_path = tmp.name

    print(f"📷 Временный файл сохранен: {temp_path}")
    print(f"🧠 Prompt: {prompt}")

    try:
        # 🛠️ Обработка изображения
        processed_path = preprocess_image(temp_path)

        # 🎬 Генерация видео
        response = client.image_to_video_v2(image_path=processed_path, prompt=prompt)
        print("✅ Ответ получен от PixVerse:", response)
        return response

    except Exception as e:
        print("❌ Ошибка при вызове image_to_video:", e)
        return {"detail": f"Ошибка генерации видео: {e}"}
@router.get("/generate-status")
async def generate_status(task_id: str):
    try:
        response = client.get_video_status(task_id)
        return response
    except Exception as e:
        print("❌ Ошибка при получении статуса:", e)
        return {"detail": f"Ошибка получения статуса генерации: {e}"}