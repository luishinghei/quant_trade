import ccxt

from quanttrading.strategies import BaseStrat
from quanttrading.utils import log


logger = log.init_logger('pos')

class PositionEngine:
    def __init__(self, exchange: ccxt.Exchange, strategies: dict[str, list[BaseStrat]], max_positions: dict[str, float]):
        self.exchange = exchange
        self.strategies = strategies  # {symbol1: [strat1, strat2], symbol2: [strat3]}
        self.max_positions = max_positions  # {symbol1: 0.12, symbol2: 0.5}
    
    def get_equal_weighted_signal(self, symbol: str) -> float:
        signals = [strat.get_signal() for strat in self.strategies[symbol]]
        return sum(signals) / len(signals)
    
    def fetch_current_position(self, symbol: str) -> float:
        position = self.exchange.fetch_position(symbol)
        logger.info(f"{symbol} Current Position: {position['contracts']}")
        if position['side'] == 'long':
            return position['contracts']
        elif position['side'] == 'short':
            return -position['contracts']
        return 0.0
    
    def calculate_position_delta(self, symbol: str) -> float:
        signal = self.get_equal_weighted_signal(symbol)
        if not -1.0 <= signal <= 1.0:
            raise ValueError('Signal must be between -1 and 1')
        
        target_position = self.max_positions[symbol] * signal
        current_position = self.fetch_current_position(symbol)
        position_delta = target_position - current_position
        min_position = self.exchange.market(symbol)['precision']['amount']
        position_delta = 0 if abs(position_delta) < min_position else position_delta
        
        logger.info(f'{symbol} Current Pos: {current_position}, Target Pos: {target_position}, Pos Delta: {position_delta}')
        return position_delta