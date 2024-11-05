import ccxt

from quanttrading.strat_pool import StratPool
from quanttrading.data_fetcher import DataFetcher
from quanttrading.strategies import BaseStrat
from quanttrading.utils import log


logger = log.init_logger('pos')


class PositionEngine:
    def __init__(self, exchange: ccxt.Exchange, strat_pool: StratPool, data_fetcher: DataFetcher) -> None:
        self.exchange = exchange
        self.strat_pool = strat_pool
        self.data_fetcher = data_fetcher
    
    def fetch_current_pos(self, symbol: str) -> float:
        position = self.exchange.fetch_position(symbol)

        if position['side'] == 'long':
            return position['contracts']
        elif position['side'] == 'short':
            return -position['contracts']
        return 0.0
    
    def calculate_target_pos_by_strat(self, strat: BaseStrat, is_active: bool) -> float:
        """Calculates the target position for a specific strategy."""    
        if is_active:
            signal = strat.generate_signal()
        else:
            signal = self.data_fetcher.fetch_signal_from_csv(strat.strat_name)
        
        logger.info(f'{strat.id:03d} {strat.symbol} {strat.timeframe} {strat.params} {"live" if is_active else "csv"}')
        
        max_pos = strat.max_pos
        target_pos = signal * max_pos
        logger.info(f'{strat.id:03d} {strat.symbol} {strat.timeframe} Target pos: {target_pos}')
        
        return target_pos
    
    def calculate_target_pos_by_symbol(self, symbol: str, timeframe: str, is_active: bool) -> float:
        """Calculates the aggregate target position for all strategies on a symbol for a given timeframe."""
        strategies = self.strat_pool.strategies.get(symbol, {})
        target_pos = 0.0
        # logger.info(f'Calculating target position for {symbol} {timeframe} {"live" if is_active else "csv"}')
        logger.info(f'{symbol} {timeframe}, {"live" if is_active else "csv"}, calculating target position')
        
        for strat in strategies[timeframe]:
            target_pos += self.calculate_target_pos_by_strat(strat, is_active)
        
        return target_pos
    
    def calculate_pos_delta(self, symbol: str, active_tfs: list[str], inactive_tfs: list[str]) -> float:
        """Calculates the delta between the target and current position for a given symbol."""
        target_pos = 0.0
        
        # Calculate the total target position for active timeframe
        for tf in active_tfs:
            target_pos += self.calculate_target_pos_by_symbol(symbol, tf, is_active=True)
        
        # Calculate the total target position for inactive timeframes
        for tf in inactive_tfs:
            target_pos += self.calculate_target_pos_by_symbol(symbol, tf, is_active=False)
        
        current_pos = self.fetch_current_pos(symbol)
        pos_delta = target_pos - current_pos
        
        # Check minimum position precision to avoid insignificant deltas
        min_pos = self.exchange.market(symbol)['precision']['amount']
        pos_delta = 0 if abs(pos_delta) < min_pos else pos_delta
        
        logger.info(f'{symbol} current pos: {current_pos}, target pos: {target_pos}, pos delta: {pos_delta}')
        
        return pos_delta