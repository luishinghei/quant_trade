import requests

from dotenv import load_dotenv
import os

from quanttrading.utils import log


logger = log.init_logger('Telegram')

    
def _load_api_config() -> tuple[str, str]:
    load_dotenv()
    api_key = os.getenv("tg_api_key")
    chat_id = os.getenv("tg_chat_id")
    
    return api_key, chat_id


def send_message(message: str):
    api_key, chat_id = _load_api_config()
    base_url = 'https://api.telegram.org/bot'
    
    url = f'{base_url}{api_key}/sendMessage?chat_id={chat_id}&text={message}'
    requests.get(url)
    
    logger.debug(f'{message}')
