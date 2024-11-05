import yaml
import json
import os
from dataclasses import dataclass

from quanttrading.utils.log import init_logger


logger = init_logger('config')

@dataclass
class StratConfig:
    id: int
    name: str
    type: str
    symbol: str
    timeframe: str
    side: str
    max_pos: float
    params: list[dict[str, float | int]]
    order_type: str
    mdd_limit: float


class ConfigManager:
    def __init__(self, is_demo: bool = True) -> None:
        self.config = None
        self.is_demo = is_demo
        self.config_path = 'config_test/strategies.yaml' if is_demo else 'config/strategies.yaml'
    
    def load_strategy_config(self) -> list[StratConfig]:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f'Config file {self.config_path} not found.')
        
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        
            self._validate_strategy_config()
        
            strat_no = len(self.config['strategies'])
            logger.info(f"Loaded {strat_no} strategy configs")
            # return self.config
            strat_configs = []
            for strategy in self.config['strategies']:
                strat_configs.append(self.create_strat_config(strategy))
            
            return strat_configs
        
        except Exception as e:
            raise ValueError(f"Error loading strategy config: {e}")
    
    def _validate_strategy_config(self) -> None:     
        required_fields = [
            'id',
            'name',
            'type',
            'symbol',
            'timeframe',
            'side',
            'max_pos',
            'params',
            'order_type',
            'mdd_limit',
        ]
        valid_timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '4h', '8h', '1d']
        valid_sides = ['long', 'short', 'long_short']
        valid_order_types = ['market', 'limit']
        
        for strategy in self.config.get('strategies', []):
            for field in required_fields:
                if field not in strategy:
                    raise ValueError(f"Missing field '{field}' in strategy {strategy['id']}.")
            
            if strategy['timeframe'] not in valid_timeframes:
                raise ValueError(f"Invalid timeframe in strategy {strategy['id']}: {strategy['timeframe']}")
            
            if strategy['side'] not in valid_sides:
                raise ValueError(f"Invalid side in strategy {strategy['id']}: {strategy['side']}")
            
            if strategy['order_type'] not in valid_order_types:
                raise ValueError(f"Invalid order_type in strategy {strategy['id']}: {strategy['order_type']}")
            
            params = strategy.get('params', []) 
            for param in params:
                for key, value in param.items():
                    if not isinstance(value, (int, float)):
                        raise TypeError(f"Invalid type for param '{key}' in strategy {strategy['id']}.")
    
    # def get_abs_max_pos(self) -> dict[str, float]:
    #     max_pos_dict = {}
    #     for strategy in self.config['strategies']:
    #         symbol = strategy['symbol']
    #         max_pos = strategy['max_pos']
    #         if symbol in max_pos_dict:
    #             max_pos_dict[symbol] += max_pos
    #         else:
    #             max_pos_dict[symbol] = max_pos
    #     return max_pos_dict
    
    # def get_strategy_by_id(self, strategy_id: int) -> dict:
    #     for strategy in self.config['strategies']:
    #         if strategy['id'] == strategy_id:
    #             return strategy        
    #     raise ValueError(f"Strategy with id {strategy_id} not found.")
    
    # def get_strategy_by_name(self, strategy_name: str) -> dict:
    #     for strategy in self.config['strategies']:
    #         if strategy['name'] == strategy_name:
    #             return strategy
    #     raise ValueError(f"Strategy with name {strategy_name} not found.")
    
    # def get_symbols(self) -> list[str]:
    #     symbols = []
    #     for strategy in self.config['strategies']:
    #         symbol = strategy['symbol']
    #         if symbol not in symbols:
    #             symbols.append(symbol)
    #     return symbols
    
    def create_strat_config(self, strategy: dict) -> StratConfig:
        return StratConfig(
            id=strategy['id'],
            name=strategy['name'],
            type=strategy['type'],
            symbol=strategy['symbol'],
            timeframe=strategy['timeframe'],
            side=strategy['side'],
            max_pos=strategy['max_pos'],
            params=strategy['params'],
            order_type=strategy['order_type'],
            mdd_limit=strategy['mdd_limit']
        )
