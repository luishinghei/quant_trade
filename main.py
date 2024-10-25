import pandas as pd
import numpy as np
from apscheduler.schedulers.blocking import BlockingScheduler

from quanttrading.utils.log import init_logger
from quanttrading.exchange import init_exchange
from quanttrading import BaseStrat, StratManager, PositionEngine, Trader, DataFetcher, ConfigManager


logger = init_logger('bot')

class Strat01(BaseStrat):
    def calculate_signal_df(self, df: pd.DataFrame) -> pd.DataFrame:
        # z_score momentum strategy
        df['ma'] = df['close'].rolling(self.window).mean()
        df['sd'] = df['close'].rolling(self.window).std()
        df['z'] = (df['close'] - df['ma']) / df['sd']
        df['signal'] = np.where(df['z'] > self.threshold, 1, 0)
        return df

class Strat02(BaseStrat):
    def calculate_signal_df(self, df: pd.DataFrame) -> pd.DataFrame:
        # ma pct diff strategy
        df['ma'] = df['close'].rolling(self.window).mean()
        df['pct_diff'] = df['close'] / df['ma'] - 1
        df['signal'] = np.where(df['pct_diff'] > self.threshold, 1, 0)
        return df

def trading_job(trader: Trader, symbols) -> None:
    trader.trade(symbols)
    

if __name__ == '__main__':
    exchange = init_exchange()
    data_fetcher = DataFetcher(exchange)

    config_manager = ConfigManager()
    strat_configs = config_manager.load_strategy_config('config/strategies.yaml')
    max_positions = config_manager.get_abs_max_pos()
    symbols = config_manager.get_symbols()
    
    strats =[
        Strat01(strat_configs[0], data_fetcher),
        Strat02(strat_configs[1], data_fetcher),
        Strat01(strat_configs[2], data_fetcher)
    ]
    
    strat_manager = StratManager()
    strat_dict = strat_manager.create_strat_dict(symbols, strats)

    position_engine = PositionEngine(exchange, strat_dict, max_positions)
    
    trader = Trader(exchange, position_engine)
    
    schedualer = BlockingScheduler()
    schedualer.add_job(trading_job, 'cron', args=[trader, symbols], second='2,22,42', id='trading_job_btc')
    schedualer.start()