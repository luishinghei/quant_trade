import pandas as pd
import numpy as np

from abc import ABC, abstractmethod

from quanttrading.config_manager import StratConfig
from quanttrading.data_fetcher import DataFetcher
from quanttrading.utils.log import init_logger


logger = init_logger('strats')

class BaseStrat(ABC):
    def __init__(self, config: StratConfig, data_fetcher: DataFetcher):
        self.config = config
        self.data_fetcher = data_fetcher
        
        self.id = config.id
        self.name = config.name
        self.symbol = config.symbol
        self.timeframe = config.timeframe
        self.order_type = config.order_type
        self.max_pos = config.max_pos
        
        self.num_param_pairs = len(config.params)
        self.params = self.get_params_dict(config.params)  # {'window': [20, 50], 'threshold': [2, 1.5]}
        self.max_window = self.get_max_window()
        
        self.strat_name = f'{self.id:03d}-{self.name}'

        self.init_data()

    def init_data(self) -> None:
        """Fetches alpha, calculates signals, and exports to CSV."""
        df = self.fetch_alpha()
        df = self.calculate_agg_signal_df(df)
        
        # logger.info(f'Initilaized {self.strat_name} strategy with {self.num_param_pairs} parameter pairs')
        logger.info(f'{self.id:03d} {self.symbol} {self.timeframe}, initialized {self.strat_name} strategy, {self.num_param_pairs} param pairs')
         
    def get_params_dict(self, params_list: list[dict]) -> dict[str, list]:
        """Converts a list of dictionaries to a dictionary of lists."""
        return {key: [d[key] for d in params_list] for key in params_list[0]}
    
    def get_max_window(self) -> int:
        """Returns the maximum window parameter."""
        return max(self.params['window'])
    
    def calculate_agg_signal_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculates the aggregated signals for multiple parameter sets and adds them to DataFrame."""
        df = df.copy()
        signals_df = pd.DataFrame(index=df.index)
        
        for param_set in zip(*self.params.values()):
            param_dict = dict(zip(self.params.keys(), param_set))
            
            # Calculate signal for each parameter set
            df_temp = self.calculate_signal_df(df, **param_dict)
            
            # Export signal to CSV
            strat_param_name = f"{self.strat_name}-" + "-".join(f'{v}' for v in param_dict.values())
            self.data_fetcher.to_signal_csv(df_temp, strat_param_name)
            signal = df_temp['signal'].iloc[-1]
            logger.info(f'{self.id:03d} {self.symbol} {self.timeframe} {param_dict} Signal: {signal}')
            
            # Concatenate signals to DataFrame
            col_name = f'signal_' + '-'.join(f'{v}' for v in param_dict.values())
            signals_df[col_name] = df_temp['signal']
            
        # Aggregate signals
        signals_df['signal'] = signals_df.mean(axis=1)
        signal = signals_df['signal'].iloc[-1]
        logger.info(f'{self.id:03d} {self.symbol} {self.timeframe} Signal(agg): {signal}')
        
        # Export aggregated signal to CSV
        self.data_fetcher.to_signal_csv(signals_df, self.strat_name)
        
        return signals_df  # Return the DataFrame containing all signals
    
    def calculate_z_score(self, df: pd.DataFrame, window) -> pd.DataFrame:
        window = int(window)
        df['ma'] = df['close'].rolling(window).mean()
        df['std'] = df['close'].rolling(window).std()
        df['z'] = (df['close'] - df[f'ma']) / df[f'std']
        return df

    def calculate_ma_pct_diff(self, df: pd.DataFrame, window) -> pd.DataFrame:
        window = int(window)
        df['ma'] = df['close'].rolling(window).mean()
        df['pct_diff'] = df['close'] / df['ma'] - 1
        return df

    def generate_signal(self) -> float:
        """Fetches data, calculates signal, logs it, and returns the latest signal."""
        df = self.fetch_alpha()
        df = self.calculate_agg_signal_df(df)
        
        return df['signal'].iloc[-1]
    
    # def log_signal_from_df(self, df: pd.DataFrame, strat_name: float) -> None:
    #     """Logs the signal based on its value."""
    #     signal = df['signal'].iloc[-1]
    #     # log_type = "[ NEUTRAL ]" if signal == 0 else "[ LONG ]" if signal > 0 else "[ SHORT ]"
    #     # logger.info(f'{log_type} {strat_name}: signal = {signal}')
    #     logger.info(f'{self.id} {self.symbol} {self.timeframe} Signal: {signal}')
            
    @abstractmethod
    def fetch_alpha(self) -> pd.DataFrame:
        """Fetches the alpha data for the strategy from the DataFetcher."""
        pass
    
    @abstractmethod
    def calculate_signal_df(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    def __repr__(self):
        return f'{self.name} srtategy'
    
    # def calculate_pnl_df(self, df: pd.DataFrame, cost_in_bp: float = 0.05) -> pd.DataFrame:
    #     df['position'] = df['signal'].shift(1)
    #     df['cost'] = df['position'].diff().abs() * cost_in_bp / 100
    #     df['pnl'] = df['position'] * df['close'].pct_change() - df['cost']
    #     df['cum_pnl'] = df['pnl'].cumsum()
    #     return df
    

    
# class Strat002(BaseStrat):
#     def fetch_data(self) -> pd.DataFrame:
#         return self.data_fetcher.fetch_historical_prices(self.symbol, self.timeframe, limit=self.window)
        
#     def calculate_signal_df(self, df: pd.DataFrame, threshold) -> pd.DataFrame:
#         df = self.calculate_ma_pct_diff(df)
#         df['signal'] = np.where(df['pct_diff'] > threshold, 1, 0)
#         return df