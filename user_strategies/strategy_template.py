import pandas as pd
import numpy as np
from quanttrading import BaseStrat


class AwesomeSrtat(BaseStrat):
    def fetch_alpha(self) -> pd.DataFrame:
        ...
    
    def calculate_signal_df(self, df: pd.DataFrame) -> pd.DataFrame:
        ...
