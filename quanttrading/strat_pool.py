from quanttrading.strategies import BaseStrat
from quanttrading.utils import log


logger = log.init_logger('pool')

class StratPool:
    timeframe_order = {
        '1m': 60,
        '3m': 180,
        '5m': 300,
        '15m': 900,
        '30m': 1800,
        '1h': 3600,
        '4h': 14400,
        '8h': 28800,
        '1d': 86400,
    }
    
    def __init__(self):
        self.strategies = {}  # Outout dict: {symbol: {timeframe: [strategies]}}
        # {'BTCUSDT': {'3m': [3m_z_score_mom srtategy],
        #             '1m': [1m_ma_pct_diff_reversal srtategy],
        #             '5m': [5m_z_score_mom srtategy]},
        # 'ETHUSDT': {'1m': [1m_z_score_mom srtategy], '3m': [3m_z_score_mom srtategy]},
        # 'BNBUSDT': {'3m': [3m_z_score_mom srtategy]}}    
    
    def add_strategy(self, strat: BaseStrat) -> None:
        if strat.symbol not in self.strategies:
            self.strategies[strat.symbol] = {}
        
        if strat.timeframe not in self.strategies[strat.symbol]:
            self.strategies[strat.symbol][strat.timeframe] = []
        
        self.strategies[strat.symbol][strat.timeframe].append(strat)
    
    def add_strategies(self, strats: list[BaseStrat]) -> None:
        for strat in strats:
            self.add_strategy(strat)
    
    def get_timeframes_for_symbol(self, symbol: str) -> list[str]:
        """Get a sorted list of all the timeframes available for a given symbol, sorted by timeframe order."""
        if symbol not in self.strategies:
            return []
        
        timeframes = self.strategies[symbol].keys()
        return sorted(timeframes, key=lambda tf: self.timeframe_order[tf])
    
    # def get_strategies(self, symbol: str, timeframe: str) -> list[BaseStrat]:
    #     return self.strategies[symbol][timeframe]
    
    # def get_strategies_by_timeframe(self) -> dict:
    #     # Outout dict: {timeframe: {symbol: [strategies]}}
    #     # {'1m': {'BTCUSDT': [1m_ma_pct_diff_reversal srtategy],
    #     #         'ETHUSDT': [1m_z_score_mom srtategy]},
    #     # '3m': {'BTCUSDT': [3m_z_score_mom srtategy],
    #     #         'ETHUSDT': [3m_z_score_mom srtategy]}}
    #     strategies_by_timeframe = {}
        
    #     for symbol, symbol_timeframes in self.strategies.items():
    #         for timeframe, strategies in symbol_timeframes.items():
    #             if timeframe not in strategies_by_timeframe:
    #                 strategies_by_timeframe[timeframe] = {}
                
    #             strategies_by_timeframe[timeframe][symbol] = strategies
        
    #     return strategies_by_timeframe
    
    
    def get_timeframes(self) -> list[str]:
        """Get a sorted list of all the timeframes available in the pool, sorted by timeframe order."""
        timeframes = set()  # Use a set to avoid duplicate timeframes
        for symbol_timeframes in self.strategies.values():
            timeframes.update(symbol_timeframes.keys())
            
        return sorted(timeframes, key=lambda tf: self.timeframe_order[tf])
    

    
    # def get_higher_timeframes(self, current_timeframe: str) -> list[str]:
    #     """Get a sorted list of timeframes starting from the current timeframe and including all higher timeframes."""
    #     timeframes = self.get_timeframes()
        
    #     if current_timeframe not in timeframes:
    #         raise ValueError(f"{current_timeframe} is not a valid timeframe in the pool.")
        
    #     idx = timeframes.index(current_timeframe)
    #     return timeframes[idx:]
    
    # def get_higher_timeframes_for_symbol(self, symbol: str, current_timeframe: str) -> list[str]:
    #     """Get a sorted list of timeframes starting from the current timeframe and including all higher timeframes."""
    #     timeframes = self.get_timeframes_for_symbol(symbol)
    #     idx = timeframes.index(current_timeframe)
    #     return timeframes[idx:]
    
    # def get_lower_timeframes(self, current_timeframe: str) -> list[str]:
    #     """Get a sorted list of timeframes starting from the current timeframe and including all lower timeframes."""
    #     timeframes = self.get_timeframes()
        
    #     if current_timeframe not in timeframes:
    #         raise ValueError(f"{current_timeframe} is not a valid timeframe in the pool.")
        
    #     idx = timeframes.index(current_timeframe)
    #     return timeframes[:idx+1]