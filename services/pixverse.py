import requests
import uuid
import os
from services.Telegram import send_telegram_alert
from PIL import Image

class PixVerseClient:
    def __init__(self, api_key: str, app_bundle_id: str, apphud_user_id: str):
        self.api_key = "sk-26eac1353e1ec9ddde1a42ed195e191f"
        self.bundle_id = "ai.pixverse.web"
        self.apphud_user_id = "i90172142"
        self.base_url = "https://app-api.pixverse.ai/openapi/v2"

    def _generate_trace_id(self):
        return str(uuid.uuid4())

    def _headers(self):
        return {
            "API-KEY": self.api_key,
            "Ai-trace-id": self._generate_trace_id()
        }

    def _handle_response(self, response):
        try:
            response.raise_for_status()
            json_resp = response.json()
            if json_resp.get("ErrCode", 0) != 0:
                send_telegram_alert(f"API вернул ошибку: {json_resp}")
            return json_resp
        except requests.RequestException as e:
            send_telegram_alert(f"HTTP ошибка: {str(e)}\nОтвет: {response.text}")
            return {"ErrCode": -1, "ErrMsg": str(e), "Resp": None}
        except Exception as ex:
            send_telegram_alert(f"Непредвиденная ошибка: {str(ex)}")
            return {"ErrCode": -2, "ErrMsg": "Unknown error", "Resp": None}

    def get_credit_balance(self):
        url = f"{self.base_url}/account/balance"
        headers = self._headers()
        response = requests.get(url, headers=headers)
        print("📊 Ответ от PixVerse (balance):", response.status_code, response.text)

        json_data = self._handle_response(response)
        if json_data["ErrCode"] == 0:
         resp = json_data["Resp"]
         print(f"💰 Текущий баланс: {resp.get('credit_monthly')} (Подписка), {resp.get('credit_package')} (Покупные), ID: {resp.get('account_id')}")
         return json_data


    def text_to_video(self, prompt: str, duration: int = 5, quality: str = "540p"):
        balance = self.get_credit_balance()
        credit_monthly = balance.get("Resp", {}).get("credit_monthly", 0)
        credit_package = balance.get("Resp", {}).get("credit_package", 0)
        total_credits = credit_monthly + credit_package

        if total_credits <= 0:
            return {
                "ErrCode": 500090,
                "ErrMsg": "❌ Недостаточно кредитов для генерации видео (text_to_video).",
                "Resp": None
            }

        url = f"{self.base_url}/video/text/generate"
        headers = self._headers()
        headers["Content-Type"] = "application/json"

        data = {
            "prompt": prompt,
            "duration": duration,
            "quality": quality,
            "model": "v3.5",
            "motion_mode": "normal",
            "aspect_ratio": "16:9",
            "seed": 0,
            "water_mark": False,
            "app_bundle_id": self.bundle_id,
            "apphud_user_id": self.apphud_user_id
        }

        print("📤 Отправляем данные:", data)
        response = requests.post(url, headers=headers, json=data)
        print("📝 Ответ от PixVerse (text2video):", response.status_code, response.text)
        return self._handle_response(response)

    def image_to_video_v2(self, image_path: str, prompt: str, duration: int = 5, quality: str = "360p"):
        # 1. Загрузка изображения
        url_upload = f"{self.base_url}/image/upload"
        headers = self._headers()

        with open(image_path, 'rb') as f:
            filename = os.path.basename(image_path)
            files = {'image': (filename, f, 'image/jpeg')}
            response_upload = requests.post(url_upload, headers=headers, files=files)

        print("📤 Ответ от PixVerse (upload):", response_upload.status_code, response_upload.text)

        if response_upload.status_code != 200:
            return {"ErrCode": -1, "ErrMsg": "Image upload failed", "Resp": response_upload.text}

        img_id = response_upload.json().get("Resp", {}).get("img_id")
        if not img_id:
            return {"ErrCode": -2, "ErrMsg": "No img_id returned", "Resp": response_upload.json()}

        # 2. Генерация видео
        url_video = f"{self.base_url}/video/img/generate"
        headers["Content-Type"] = "application/json"
        data = {
            "prompt": prompt,
            "img_id": img_id,
            "duration": duration,
            "quality": quality,
            "model": "v3.5",
            "motion_mode": "normal",
            "negative_prompt": "",
            "seed": 0,
            "water_mark": False,
            "app_bundle_id": self.bundle_id,
            "apphud_user_id": self.apphud_user_id
        }

        response_video = requests.post(url_video, headers=headers, json=data)
        print("🎬 Ответ от PixVerse (video):", response_video.status_code, response_video.text)
        return self._handle_response(response_video)

    def get_video_status(self, task_id: str):
        url = f"{self.base_url}/video/query"
        headers = self._headers()
        params = {
            "task_id": task_id,
            "app_bundle_id": self.bundle_id,
            "apphud_user_id": self.apphud_user_id
        }

        response = requests.get(url, headers=headers, params=params)
        print("📡 Ответ от PixVerse (status):", response.status_code, response.text)
        return self._handle_response(response)
