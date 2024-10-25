import ccxt

from quanttrading.position_engine import PositionEngine
from quanttrading.utils import log


logger = log.init_logger('trader')

class Trader():
    def __init__(self, exchange: ccxt.Exchange, position_engine: PositionEngine):
        self.exchange = exchange
        self.position_engine = position_engine
    
    def upper_symbols(self, symbols: list[str]) -> None:
        # Capitalize all symbols
        return [symbol.upper() for symbol in symbols]
        
    def trade(self, symbols: list[str]) -> None:
        symbols = self.upper_symbols(symbols)
        for symbol in symbols:
            position_delta = self.position_engine.calculate_position_delta(symbol)
            self.trade_per_symbol(symbol, position_delta, type='market')
    
    def trade_per_symbol(self, symbol: str, position_delta: float, type='market') -> None:
        if position_delta == 0:
            logger.info(f'No {symbol} trade required')
        else:
            side = 'buy' if position_delta > 0 else 'sell'
            if type == 'market':
                self.exchange.create_order(symbol=symbol, type=type, side=side, amount=abs(position_delta))
                
                logger.info(f'Created a {side} {type} order for {abs(position_delta)} {symbol} contracts')
            elif type == 'limit':
                best_bid = self.fetch_best_bid(symbol)
                self.exchange.create_order(symbol=symbol, type='limit', side=side, amount=abs(position_delta), price=best_bid)
                
                logger.info(f'Created a {side} {type} order for {abs(position_delta)} {symbol} contracts at {best_bid}')
            else:
                raise ValueError('Invalid order type')
            
        updated_position = self.position_engine.fetch_current_position(symbol)
        logger.info(f'{symbol} Updated position: {updated_position}')

    def fetch_best_bid(self, symbol: str) -> float:
        orderbook = self.exchange.fetch_order_book(symbol, limit=1)
        best_bid = orderbook['bids'][0][0]
        return best_bid