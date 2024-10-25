import pandas as pd

from quanttrading.config_manager import StratConfig
from quanttrading.data_fetcher import DataFetcher
from quanttrading.utils.log import init_logger


logger = init_logger('strats')

class BaseStrat:
    def __init__(self, config: StratConfig, data_fetcher: DataFetcher):
        self.config = config
        self.name = config.name
        self.symbol = config.symbol
        self.timeframe = config.timeframe
        self.params = config.params[0]  # Assume only one set of params for now {'threshold': 2.0, 'window': 20}
        self.data_fetcher = data_fetcher
        
        for key, value in self.params.items():
            setattr(self, key, value)
        
        self.init_data()
    
    def init_data(self) -> None:
        df = self.data_fetcher.fetch_historical_prices(self.symbol, self.timeframe, limit=self.window)
        df = self.calculate_signal_df(df)
        # df = self.calculate_pnl_df(df)
        
        file_path = f'user_data/data/{self.name}_{self.symbol}_{self.timeframe}.csv'
        # df.to_csv(file_path)
        self.data_fetcher.to_signal_csv(df, file_path)
        
        logger.info(f'Initilaized {self.name} {self.symbol} {self.timeframe} strategy')
    
    def calculate_pnl_df(self, df: pd.DataFrame, cost_in_bp: float = 0.05) -> pd.DataFrame:
        df['position'] = df['signal'].shift(1)
        df['cost'] = df['position'].diff().abs() * cost_in_bp / 100
        df['pnl'] = df['position'] * df['close'].pct_change() - df['cost']
        df['cum_pnl'] = df['pnl'].cumsum()
        return df
    
    def get_signal(self) -> float:
        df = self.data_fetcher.fetch_historical_prices(self.symbol, self.timeframe, limit=self.window)
        df = self.calculate_signal_df(df)
        # df = self.calculate_pnl_df(df)
        self.data_fetcher.to_signal_csv(df, f'user_data/data/{self.name}_{self.symbol}_{self.timeframe}.csv')
        
        signal = df['signal'].iloc[-1]
        self.log_signal(signal)
        
        return signal
    
    def log_signal(self, signal: float) -> None:
        if signal == 0:
            logger.info(f'[ NEUTRAL ] {self.name}: signal = {signal}')
        elif signal > 0:
            logger.info(f'[ LONG ] {self.name}: signal = {signal}')
        else:
            logger.info(f'[ SHORT ] {self.name}: signal = {signal}')
    
    def calculate_signal_df(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

    def __repr__(self):
        return f'{self.name} srtategy'

class StratManager():
    def create_strat_dict(self, symbols: list[str], strategies: list[BaseStrat]) -> dict:
        strat_dict = {}
        for symbol in symbols:
            strat_dict[symbol.upper()] = []
            for strategy in strategies:
                if strategy.symbol == symbol:
                    strat_dict[symbol.upper()].append(strategy)
        return strat_dict