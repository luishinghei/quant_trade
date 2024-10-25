import pandas as pd
import ccxt
import os
from datetime import datetime

from quanttrading.utils.log import init_logger
from quanttrading.utils.api import load_api_config


logger = init_logger('exchange')

def init_exchange(enable_demo_trading: bool = True) -> ccxt.Exchange:
    api_key, api_secret = load_api_config()
    
    exchange = ccxt.bybit({
        'apiKey': api_key,
        'secret': api_secret,
    })
    logger.info('Connected to Bybit')
    
    if enable_demo_trading:
        exchange.enable_demo_trading(True)
        logger.info('Demo trading enabled')
    
    exchange.load_markets()
    logger.info('Markets loaded')
    
    return exchange