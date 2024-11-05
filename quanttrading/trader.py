import ccxt

import time

from quanttrading.position_engine import PositionEngine
from quanttrading.strat_pool import StratPool
from quanttrading.utils import log


logger = log.init_logger('trader')

class Trader():
    def __init__(self, exchange: ccxt.Exchange, position_engine: PositionEngine, strat_pool: StratPool) -> None:
        self.exchange = exchange
        self.position_engine = position_engine
        self.strat_pool = strat_pool
        self.active_tf_dict = {
            '1m': False,
            '3m': False,
            '5m': False,
            '15m': False,
            '30m': False,
            '1h': False,
            '4h': False,
            '8h': False,
            '1d': False,
        }
    
    def activate_timeframe(self, timeframe: str) -> None:
        """Set the state of the current timeframe and the lower timeframes to True"""
        self.active_tf_dict[timeframe] = True
        
        logger.info(f'activated {timeframe} trading session')
    
    def deactivate_timeframes(self) -> None:
        """Reset the state of all timeframes to False"""
        for timeframe in self.active_tf_dict.keys():
            self.active_tf_dict[timeframe] = False
        
        logger.info('deactivated all trading sessions')
    
    def get_active_timeframes(self) -> list[str]:
        """Get the list of active timeframes"""
        return [timeframe for timeframe, is_active in self.active_tf_dict.items() if is_active]
    
    def get_active_timeframes_for_symbol(self, symbol: str) -> list[str]:
        """Get the list of active timeframes for a specific symbol"""
        return [timeframe for timeframe in self.get_active_timeframes() if timeframe in self.strat_pool.strategies[symbol]]
    
    def trade_by_symbol(self, symbol: str, active_tfs: list[str], inactive_tfs: list[str], type='limit') -> None:
        pos_delta = self.position_engine.calculate_pos_delta(symbol, active_tfs, inactive_tfs)

        if pos_delta == 0:
            logger.debug(f'No {symbol} trade required')
            return
        
        side = 'buy' if pos_delta > 0 else 'sell'
        self.place_order(symbol, side, abs(pos_delta), type)
        
        updated_position = self.position_engine.fetch_current_pos(symbol)
        logger.info(f'{symbol} Updated position: {updated_position}')
    
    def place_order(self, symbol: str, side: str, amount: float, type: str) -> None:
        if type == 'market':
            self.exchange.create_order(symbol=symbol, type=type, side=side, amount=amount)
            logger.info(f'Created a {side} {type} order for {amount} {symbol} contracts')
        elif type == 'limit':
            best_bid = self.fetch_best_bid(symbol)
            self.exchange.create_order(symbol=symbol, type=type, side=side, amount=amount, price=best_bid)
            logger.info(f'Created a {side} {type} order for {amount} {symbol} contracts at {best_bid}')
        else:
            raise ValueError('Invalid order type')
    
    def trade(self, delay: float | None = None) -> None:
        if delay:
            time.sleep(delay)
        
        active_tfs = self.get_active_timeframes()
        if not active_tfs:
            logger.info('No active trading sessions')
            return
        
        logger.info(f'{active_tfs} trading session start')
       
        for symbol in self.strat_pool.strategies.keys():
            symbol_active_tfs = self.get_active_timeframes_for_symbol(symbol)
            
            # Skip if no active timeframes for the symbol
            if not symbol_active_tfs:
                continue
            
            symbol_tfs = self.strat_pool.get_timeframes_for_symbol(symbol)
            symbol_inactive_tfs = [tf for tf in symbol_tfs if tf not in symbol_active_tfs]
            
            logger.info(f'{symbol}, active_tfs: {symbol_active_tfs}, inactive_tfs: {symbol_inactive_tfs}')
            self.trade_by_symbol(symbol, symbol_active_tfs, symbol_inactive_tfs)
        
        logger.info(f'{active_tfs} trading session completed')
        
        self.deactivate_timeframes()
        
    def fetch_best_bid(self, symbol: str) -> float:
        orderbook = self.exchange.fetch_order_book(symbol, limit=1)

        if not orderbook['bids']:
            logger.error(f'No bids available for {symbol}')
            raise ValueError(f'No bids available for {symbol}')
        
        return orderbook['bids'][0][0]
