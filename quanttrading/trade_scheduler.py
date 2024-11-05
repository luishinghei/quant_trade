from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

from quanttrading.utils import log
from quanttrading.strat_pool import StratPool
from quanttrading.trader import Trader


logger = log.init_logger('scheduler')

class TradeScheduler:
    def __init__(self, scheduler, trader: Trader, stratpool: StratPool) -> None:
        self.scheduler = scheduler
        self.trader = trader
        self.stratpool = stratpool
        self.timeframes = self.stratpool.get_timeframes()  # ['1m', '3m', '5m']
    
    def add_jobs(self) -> None:
        for tf in self.timeframes:
            func = getattr(self, f'add_{tf}_job')
            func()
            
            logger.info(f'Added activate {tf} job')
    
    def add_1m_job(self) -> None:
        self.scheduler.add_job(
            func=self.trader.activate_timeframe,
            trigger='cron',
            args=['1m'],
            second='0',
            id='activate_1m'
        )

    def add_3m_job(self) -> None:
        self.scheduler.add_job(
            func=self.trader.activate_timeframe,
            trigger='cron',
            args=['3m'],
            minute='*/3',
            id='activate_3m'
        )

    def add_5m_job(self) -> None:
        self.scheduler.add_job(
            func=self.trader.activate_timeframe,
            trigger='cron',
            args=['5m'],
            minute='*/5',
            id='activate_5m'
        )
        
    def add_15m_job(self) -> None:
        self.scheduler.add_job(
            func=self.trader.activate_timeframe,
            trigger='cron',
            args=['15m'],
            minute='*/15',
            id='activate_15m'
        )
        
    def add_30m_job(self) -> None:
        self.scheduler.add_job(
            func=self.trader.activate_timeframe,
            trigger='cron',
            args=['30m'],
            minute='*/30',
            id='activate_30m'
        )
        
    def add_1h_job(self) -> None:
        self.scheduler.add_job(
            func=self.trader.activate_timeframe,
            trigger='cron',
            args=['1h'],
            minute=0,
            id='activate_1h'
        )
        
    def add_4h_job(self) -> None:
        self.scheduler.add_job(
            func=self.trader.activate_timeframe,
            trigger='cron',
            args=['4h'],
            hour='*/4',
            id='activate_4h'
        )
        
    def add_8h_job(self) -> None:
        self.scheduler.add_job(
            func=self.trader.activate_timeframe,
            trigger='cron',
            args=['8h'],
            hour='*/8',
            id='activate_8h'
        )
        
    def add_1d_job(self) -> None:
        self.scheduler.add_job(
            func=self.trader.activate_timeframe,
            trigger='cron',
            args=['1d'],
            hour=0,
            id='activate_1d'
        )
        