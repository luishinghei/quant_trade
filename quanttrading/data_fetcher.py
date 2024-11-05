import ccxt
import pandas as pd
import os

from quanttrading.utils.log import init_logger


logger = init_logger('data')

class DataFetcher:
    def __init__(self, exchange: ccxt.Exchange, folder: str = 'user_data') -> None:
        self.exchange = exchange
        self.user_data_folder = folder
        
        self.csv_folder = f'{folder}/data'
        os.makedirs(self.csv_folder, exist_ok=True)
    
    def fetch_historical_prices(self, symbol: str, timeframe: str, since: int | None = None, limit: int | None = None) -> pd.DataFrame:
        try:
            logger.debug(f'Fetching historical klines for {symbol} {timeframe} since {since} with limit {limit}')
            data = self.exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, since=since , limit=limit)
        except Exception as e:
            logger.error(f'Error fetching ohlcv data: {e}')
            raise e
        
        return self.process_ohlcv_data(data)
    
    def fetch_funding_rate_history(self, symbol: str, since: int | None = None, limit: int | None = None) -> pd.DataFrame:
        try:
            logger.debug(f'Fetching funding rate history for {symbol} since {since} with limit {limit}')
            funding_rates = self.exchange.fetch_funding_rate_history(symbol=symbol, since=since, limit=limit)
            
        except Exception as e:
            logger.error(f'Error fetching funding rate history: {e}')
            raise e
        
        return self.process_funding_rate_history(funding_rates)
    
    def process_ohlcv_data(self, data: list) -> pd.DataFrame:
        columns = ['timestamp', 'close']
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])[columns]
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        logger.debug(f'Processed {len(df)} rows of data')
        return df
    
    def process_funding_rate_history(self, funding_rates: list[dict]) -> pd.DataFrame:
        df = pd.DataFrame(funding_rates)
        df = df[['timestamp', 'fundingRate']]
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        df.rename(columns={'fundingRate': 'funding_rate'}, inplace=True)
        return df
    
    def to_signal_csv(self, df: pd.DataFrame, strat_name: str) -> None:
        file_path = f'{self.csv_folder}/{strat_name}.csv'
        
        if df is None or df.empty:
            logger.info(f'No data to save for {strat_name} strategy')
            df =pd.DataFrame()
        
        if not os.path.exists(file_path):
            df.to_csv(file_path)
            logger.info(f'Saved {len(df)} rows for {strat_name} strategy')
        else:
            old_df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            combined_df = pd.concat([old_df, df])
            combined_df = combined_df[~combined_df.index.duplicated(keep='last')]
            
            combined_df.to_csv(file_path)
            appended_rows = len(combined_df) - len(old_df)
            
            if appended_rows == 0:
                logger.debug(f'Updated latest data for {strat_name} strategy')
            else:
                logger.debug(f'Appended {appended_rows} rows of data for {strat_name} strategy')
    
    def fetch_signal_from_csv(self, strat_name: str) -> float:
        file_path = f'{self.csv_folder}/{strat_name}.csv'
        
        if not os.path.exists(file_path):
            logger.info(f'No csv for {strat_name} strategy')
            raise FileNotFoundError(f'No csv for {strat_name} strategy')
        else:
            df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            signal = df['signal'].iloc[-1]
            # logger.info(f'Fetched {signal} signal for {strat_name} strategy')
            return signal