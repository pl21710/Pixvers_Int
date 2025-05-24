1. Введение

Данная документация описывает работу с PixVerse API для генерации видео по тексту или изображению.

2. Общие требования

Язык: Python 3.8+

HTTP Client: requests

Требуется API-KEY для каждого запроса

Дополнительный header: ai-trace-id (случайный UUID)

3. Автентификация
Header:
API-KEY: <your-api-key>
ai-trace-id: <uuid>

4. Методы API

4.1. Получение баланса
GET /openapi/v2/account/balance
Ответ:

{
  "ErrCode": 0,
  "ErrMsg": "success",
  "Resp": {
    "account_id": 12345678,
    "credit_monthly": 100,
    "credit_package": 500
  }
}
4.2. Текст в видео

POST /openapi/v2/video/text/generate
{
  "prompt": "A wolf in the snow",
  "duration": 5,
  "quality": "360p"
}
Ответ:

{
  "ErrCode": 0,
  "ErrMsg": "success",
  "Resp": {
    "video_id": 123456789
  }
}

4.3. Загрузка изображения

POST /openapi/v2/image/upload

FormData: image: <binary file>

Ответ:

{
  "ErrCode": 0,
  "ErrMsg": "success",
  "Resp": {
    "img_id": 987654321
  }
}
4.4. Генерация видео из изображения

POST /openapi/v2/video/img/generate

{
  "img_id": 987654321,
  "prompt": "A magical forest",
  "duration": 5,
  "quality": "540p"
}

Ответ:

{
  "ErrCode": 0,
  "ErrMsg": "success",
  "Resp": {
    "video_id": 123456789
  }
}
4.5. Статус видео

GET /openapi/v2/video/status?video_id=123456789

Ответ:

{
  "ErrCode": 0,
  "ErrMsg": "success",
  "Resp": {
    "status": "done",
    "video_url": "https://..."
  }
}
5. Формат ошибок

{
  "ErrCode": <int>,
  "ErrMsg": <string>
}

Ошибки:

ErrCode

ErrMsg

Причина

401

Invalid API Key

Неверный ключ

403

No credits available

Нехватка кредитов

500

Internal Server Error

Ошибка на стороне сервера
6. Ограничения и лимиты

Лимиты по кредитам: зависит от тарифа

Частота запросов: не чаще 1 запроса/сек

Размер изображений: не более 4000x4000 px
7. Тестирование через Postman

Все методы доступны через Postman:

Добавь в Postman новую collection

Укажи API-KEY и ai-trace-id в Headers

Вызов сервисов по URL, пример: https://app-api.pixverse.ai/openapi/v2/video/status?video_id=...
Заключение

Система поддерживает полноценную интеграцию с PixVerse и готова к дополнениям при изменении API.

