import pandas as pd
import numpy as np
from quanttrading import BaseStrat


class Strat001(BaseStrat):
    def fetch_alpha(self) -> pd.DataFrame:
        return self.data_fetcher.fetch_funding_rate_history(self.symbol, limit=self.max_window)
    
    def calculate_signal_df(self, df: pd.DataFrame, window, threshold) -> pd.DataFrame:
        df['signal'] = np.where(df['funding_rate'] < threshold, -1, 0)
        return df