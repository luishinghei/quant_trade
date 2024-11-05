import pandas as pd
import numpy as np
from apscheduler.schedulers.blocking import BlockingScheduler

from quanttrading.exchange import init_exchange
from quanttrading import PositionEngine, Trader, DataFetcher, ConfigManager, StratPool, TradeScheduler
from user_strategies import (
    Strat001,
    Strat002,
    Strat003,
)

FOLDER = 'user_data_test'

exchange = init_exchange(is_demo=True)

config_man = ConfigManager(is_demo=False)
strat_configs = config_man.load_strategy_config()

data_fetcher = DataFetcher(exchange, FOLDER)


strats =[
    Strat001(strat_configs[0], data_fetcher),
    Strat002(strat_configs[1], data_fetcher),
    Strat003(strat_configs[2], data_fetcher),
]

strat_pool = StratPool()
strat_pool.add_strategies(strats)

pos_engine = PositionEngine(exchange, strat_pool, data_fetcher)

trader = Trader(exchange, pos_engine, strat_pool)

scheduler = BlockingScheduler()

trade_scheduler = TradeScheduler(scheduler, trader, strat_pool)
trade_scheduler.add_jobs()

scheduler.add_job(trader.trade, 'cron', second='0', args=[0.5], id='trade')


scheduler.start()