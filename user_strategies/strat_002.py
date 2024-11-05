import pandas as pd
import numpy as np
from quanttrading import BaseStrat


class Strat002(BaseStrat):
    def fetch_alpha(self) -> pd.DataFrame:
        return self.data_fetcher.fetch_historical_prices(self.symbol, self.timeframe, limit=self.max_window)
    
    def calculate_signal_df(self, df: pd.DataFrame, window, threshold) -> pd.DataFrame:
        df = self.calculate_z_score(df, window)
        df['signal'] = np.where(df['z'] > threshold, 1, 0)
        return df