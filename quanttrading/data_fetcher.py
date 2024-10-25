import ccxt
import pandas as pd
import os

from quanttrading.utils.log import init_logger


logger = init_logger('data')

class DataFetcher:
    def __init__(self, exchange: ccxt.Exchange):
        self.exchange = exchange
        
        data_folder = 'user_data/data'
        os.makedirs(data_folder, exist_ok=True)
    
    def fetch_historical_prices(self,
                                symbol: str,
                                timeframe: str,
                                since: int | None = None,
                                limit: int | None = None
                                ) -> pd.DataFrame:
        try:
            logger.debug(f'Fetching historical klines for {symbol} {timeframe} since {since} with limit {limit}')
            data = self.exchange.fetch_ohlcv(symbol=symbol.upper(), timeframe=timeframe, since=since , limit=limit)
        except Exception as e:
            logger.error(f'Error fetching data: {e}')
            raise e
        
        return self.process_ohlcv_data(data)
    
    def process_ohlcv_data(self, data: list) -> pd.DataFrame:
        columns = ['timestamp', 'close']
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])[columns]
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        logger.debug(f'Processed {len(df)} rows of data')
        return df
    
    def to_signal_csv(self, df: pd.DataFrame, file_path: str) -> None:
        df.dropna(inplace=True)
        
        if not os.path.exists(file_path):
            df.to_csv(file_path)
            logger.info(f'Saved {len(df)} rows to {file_path}')
        else:
            old_df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            combined_df = pd.concat([old_df, df])
            combined_df = combined_df[~combined_df.index.duplicated(keep='last')]
            
            combined_df.to_csv(file_path)
            appended_rows = len(combined_df) - len(old_df)
            
            if appended_rows == 0:
                logger.info(f'Updated the last row of {file_path}')
            else:
                logger.info(f'Appended {appended_rows} rows to {file_path}')
    
    def fetch_from_csv(self, file_path: str) -> pd.DataFrame:
        if not os.path.exists(file_path):
            logger.info(f'File {file_path} does not exist')
            return pd.DataFrame()
        else:
            df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            logger.info(f'Fetched {len(df)} rows from {file_path}')
            return df