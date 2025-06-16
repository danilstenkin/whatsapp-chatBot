import httpx
import logging
from typing import Optional
from app.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER

# Настройка логгера
logger = logging.getLogger(__name__)

async def send_whatsapp_response(to_number: str, message: str) -> bool:
    """
    Отправляет сообщение через WhatsApp Twilio API
    
    Args:
        to_number: Номер получателя в формате '+77001234567'
        message: Текст сообщения
        
    Returns:
        bool: True если сообщение отправлено успешно, False при ошибке
    """
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    
    data = {
        'From': TWILIO_WHATSAPP_NUMBER,
        'To': f'whatsapp:{to_number}',
        'Body': message
    }
    print(data)

    # Логируем начало операции (без sensitive данных)
    logger.info(f"Инициирована отправка WhatsApp сообщения на номер: {to_number[:3]}...{to_number[-2:]}")
    logger.debug(f"Полный номер получателя: {to_number}")
    logger.debug(f"Текст сообщения (первые 100 символов): {message[:100]}...")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Логируем запрос
            logger.debug(f"Отправка запроса к Twilio API: {url}")
            
            response = await client.post(url, data=data, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
            response.raise_for_status()
            
            if response.status_code == 201:
                response_data = response.json()
                sid = response_data.get("sid")
                logger.info(f"Сообщение успешно отправлено. SID: {sid}")
                logger.debug(f"Полный ответ Twilio: {response_data}")
                return True
            
            # Обработка нестандартных успешных статусов
            error_data = response.json()
            logger.error(f"Twilio API вернул неожиданный статус {response.status_code}")
            logger.error(f"Код ошибки: {error_data.get('code')}")
            logger.error(f"Сообщение: {error_data.get('message')}")
            logger.error(f"Доп. информация: {error_data.get('more_info')}")
            return False

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP ошибка при отправке сообщения")
        logger.error(f"URL: {e.request.url}")
        logger.error(f"Status Code: {e.response.status_code}")
        
        try:
            error_details = e.response.json()
            logger.error(f"Twilio Error: {error_details.get('message')}")
            logger.error(f"Error Code: {error_details.get('code')}")
        except ValueError:
            logger.error(f"Response Text: {e.response.text}")
        
        return False

    except httpx.RequestError as e:
        logger.error(f"Ошибка соединения с Twilio API")
        logger.error(f"Тип ошибки: {type(e).__name__}")
        logger.error(f"Детали: {str(e)}")
        return False

    except Exception as e:
        logger.exception(f"Неожиданная ошибка при отправке WhatsApp сообщения")
        return False