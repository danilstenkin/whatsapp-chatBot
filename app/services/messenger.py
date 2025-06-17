import httpx
from app.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER
from app.logger_config import logger

async def send_whatsapp_response(to_number: str, message: str):
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    
    data = {
        'From': TWILIO_WHATSAPP_NUMBER,
        'To': f'whatsapp:{to_number}',
        'Body': message
    }

    auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, data=data, auth=auth)
            if response.status_code == 201:
                sid = response.json().get("sid")
                logger.info(f"[TWILIO][{to_number}] - ✅ Сообщение успешно отправлено! SID: {sid}")
                return True
            else:
                error_data = response.json()
                logger.error(f"[TWILIO][{to_number}] - ❌ Ошибка отправки (код {response.status_code}): {error_data}")
                return False

    except httpx.HTTPStatusError as e:
        print(f"🚨 HTTP ошибка при отправке сообщения:")
        print(f"URL: {e.request.url}")
        print(f"Status Code: {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return False

    except httpx.RequestError as e:
        print(f"🚨 Ошибка соединения с Twilio API:")
        print(f"Request: {e.request}")
        print(f"Error: {str(e)}")
        return False

    except Exception as e:
        print(f"🚨 Неожиданная ошибка:")
        print(f"Type: {type(e).__name__}")
        print(f"Error: {str(e)}")
        return False
    

    
# import httpx
# from app.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER

# async def send_whatsapp_response(to_number: str, message: str):
#     url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"

#     data = {
#         'From': TWILIO_WHATSAPP_NUMBER,
#         'To': f'whatsapp:{to_number}',
#         'Body': message
#     }

#     auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

#     try:
#         async with httpx.AsyncClient(timeout=30.0) as client:
#             response = await client.post(url, data=data, auth=auth)

#             # ❌ НЕ вызываем raise_for_status

#             if response.status_code == 201:
#                 sid = response.json().get("sid")
#                 print(f"✅ Сообщение успешно отправлено! SID: {sid}")
#                 return True
#             else:
#                 error_data = response.json()
#                 print(f"⚠️ Не удалось отправить сообщение (status: {response.status_code})")
#                 print(f"Twilio Error: {error_data.get('message')}")
#                 print(message)
#                 return False

#     except Exception as e:
#         print(f"❗ Ошибка при отправке сообщения: {str(e)}")
#         return False
