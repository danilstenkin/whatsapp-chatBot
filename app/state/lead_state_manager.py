from app.db.utils import has_client_first_name
from app.state.lead_state import set_lead_state, set_lead_state2

async def dialog_manager(phone: str) -> str:
    state = await has_client_first_name (phone) 
    
    if state:
        await set_lead_state(phone)
        return "Имя есть в базу данных"
    else:
        await set_lead_state2(phone)
        return "Нет имени в бд"
