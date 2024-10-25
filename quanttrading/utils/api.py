from dotenv import load_dotenv
import os


def load_api_config() -> tuple[str, str]:
    load_dotenv()
    api_key = os.getenv("api_key")
    api_secret = os.getenv("api_secret")
    
    return api_key, api_secret
