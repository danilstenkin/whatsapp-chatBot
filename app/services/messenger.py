import httpx
import asyncio
from app.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER
from app.logger_config import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from aiolimiter import AsyncLimiter

# Ограничитель скорости: 1 сообщение в секунду
limiter = AsyncLimiter(1, 1)

RETRY_BASE_DELAY = 1
MAX_RETRIES = 5
TIMEOUT = 10.0

class TwilioAPIError(Exception):
    pass

@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=RETRY_BASE_DELAY, min=RETRY_BASE_DELAY, max=30),
    retry=retry_if_exception_type((httpx.RequestError, TwilioAPIError)),
    reraise=True
)
async def send_whatsapp_response(to_number: str, message: str) -> bool:
    async with limiter:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
        
        data = {
            'From': TWILIO_WHATSAPP_NUMBER,
            'To': f'whatsapp:{to_number}',
            'Body': message
        }

        headers = {
            'User-Agent': 'MyApp/1.0',
            'Accept': 'application/json'
        }

        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.post(
                    url,
                    data=data,
                    auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
                    headers=headers
                )

                if response.status_code == 201:
                    sid = response.json().get("sid")
                    logger.info(f"[TWILIO][{to_number}] Сообщение отправлено. SID: {sid}")
                    return True

                error_data = response.json()
                error_code = error_data.get('code', 'unknown')
                error_msg = error_data.get('message', 'No error message')

                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 1))
                    logger.warning(f"[TWILIO][{to_number}] Rate limit. Retry after {retry_after}s")
                    await asyncio.sleep(retry_after)
                    raise TwilioAPIError("Rate limit exceeded")

                logger.error(f"[TWILIO][{to_number}] Ошибка {error_code}: {error_msg}")
                raise TwilioAPIError(f"Twilio API error: {error_code} - {error_msg}")

        except httpx.RequestError as e:
            logger.error(f"[TWILIO][{to_number}] Сетевая ошибка: {str(e)}")
            raise
        except Exception as e:
            logger.exception(f"[TWILIO][{to_number}] Неожиданная ошибка: {str(e)}")
            raise TwilioAPIError(str(e))

    return False
