import pandas as pd
import ccxt
from dotenv import load_dotenv

from datetime import datetime
import os

from quanttrading.utils.log import init_logger
# from quanttrading.utils.api import load_api_config


logger = init_logger('exchange')

def init_exchange(is_demo: bool = True) -> ccxt.Exchange:
    try:
        api_key, api_secret = load_api(is_demo)
        exchange = ccxt.bybit({
            'apiKey': api_key,
            'secret': api_secret,
        })
        logger.info('Connected to Bybit')

        if not is_demo and not verify_passphrase():
            logger.error('Passphrase incorrect. Demo trading enabled')
            is_demo = True

        exchange.enable_demo_trading(is_demo)
        logger.info(f"{'Demo' if is_demo else 'Live'} trading enabled")

        exchange.load_markets()
        logger.info('CCXT Markets loaded')
    except Exception as e:
        logger.error(f'Error initializing exchange: {e}')
        raise e

    return exchange

# def get_trading_mode(demo_trading: bool) -> bool:
#     answer = input("Do you want to enable LIVE trading? (y/n): ")
#     return False if answer.lower() == 'y' else True

def verify_passphrase() -> bool:
    return input("Enter passphrase 'quant' for live trading: ") == 'quant'

def load_api(is_demo: bool = True) -> tuple[str, str]:
    dotenv_path = 'config_test/.env' if is_demo else 'config/.env'
    load_dotenv(dotenv_path)
    
    api_key = os.getenv('api_key')
    api_secret = os.getenv('api_secret')
    
    return api_key, api_secret