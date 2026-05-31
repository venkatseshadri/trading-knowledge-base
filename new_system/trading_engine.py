"""
Trading Engine - Orchestrates data feed, indicators, strategies, and broker
"""
import time
import logging
from datetime import datetime
from typing import Dict, Optional
import os
import sys

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../Shoonya_oAuthAPI-py'))

from feed.datafeed import DataFeed
from indicator.indicators import IndicatorEngine
from strategy.strategy import get_strategy, Signal, MultiIndicatorStrategy
from broker.broker import BrokerClient, NSE_TOKENS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TradingEngine:
    """Main trading engine that orchestrates all components"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.data_feed = None
        self.broker = None
        self.strategy = None
        self.running = False
        
    def initialize(self):
        """Initialize all components"""
        logger.info("Initializing Trading Engine...")
        
        # Initialize data feed
        self.data_feed = DataFeed()
        logger.info("✓ Data feed initialized (yfinance)")
        
        # Initialize broker
        if self.config.get('broker'):
            cred_path = self.config['broker'].get('cred_path')
            if cred_path and os.path.exists(cred_path):
                self.broker = BrokerClient(cred_path)
                self.data_feed.broker_api = self.broker.api
                logger.info(f"✓ Broker initialized: {self.broker.creds['UID']}")
            else:
                logger.warning("⚠ Broker credentials not found, running without order execution")
        
        # Initialize strategy
        strategy_name = self.config.get('strategy', 'multi')
        self.strategy = get_strategy(strategy_name)
        logger.info(f"✓ Strategy loaded: {self.strategy.name}")
        
        logger.info("Initialization complete!")
    
    def run_cycle(self) -> Dict:
        """Run one trading cycle"""
        symbol = self.config.get('symbol', '^NSEI')
        period = self.config.get('period', '5d')
        interval = self.config.get('interval', '5m')
        
        # 1. Fetch data
        ohlcv = self.data_feed.fetch_ohlcv(symbol, period, interval)
        if not ohlcv:
            return {'error': 'Failed to fetch data'}
        
        # 2. Calculate indicators
        indicators = IndicatorEngine.all_indicators(ohlcv)
        
        # 3. Evaluate strategy
        signal, scores = self.strategy.evaluate(indicators)
        
        # 4. Build result
        result = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'close': indicators['close'],
            'indicators': {
                'sma_20': round(indicators['sma_20'], 2),
                'sma_50': round(indicators['sma_50'], 2),
                'rsi_14': round(indicators['rsi_14'], 2),
                'adx_14': round(indicators['adx_14'], 2),
                'atr_14': round(indicators['atr_14'], 2),
                'bb_upper': round(indicators['bb_upper'], 2),
                'bb_middle': round(indicators['bb_middle'], 2),
                'bb_lower': round(indicators['bb_lower'], 2),
            },
            'signal': signal.value,
            'scores': scores,
        }
        
        return result
    
    def run_realtime(self, interval_seconds: int = 60):
        """Run in real-time mode"""
        self.running = True
        logger.info(f"Starting real-time mode (every {interval_seconds}s)...")
        
        while self.running:
            try:
                result = self.run_cycle()
                logger.info(f"Signal: {result.get('signal')} | Close: {result.get('close')} | RSI: {result.get('indicators', {}).get('rsi_14')}")
                
                # Sleep until next cycle
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("Stopping...")
                break
            except Exception as e:
                logger.error(f"Error in cycle: {e}")
                time.sleep(interval_seconds)
        
        self.running = False
    
    def stop(self):
        """Stop the engine"""
        self.running = False


# Configuration
DEFAULT_CONFIG = {
    'symbol': '^NSEI',
    'period': '5d',
    'interval': '5m',
    'strategy': 'multi',
    'broker': {
        'cred_path': os.path.expanduser('~/python-trader/Shoonya_oAuthAPI-py/cred.yml'),
    }
}


def main():
    """Run the trading engine"""
    config = DEFAULT_CONFIG.copy()
    
    # Allow override via args
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', default='^NSEI')
    parser.add_argument('--interval', default=60, type=int)
    parser.add_argument('--realtime', action='store_true')
    args = parser.parse_args()
    
    config['symbol'] = args.symbol
    
    # Initialize and run
    engine = TradingEngine(config)
    engine.initialize()
    
    if args.realtime:
        engine.run_realtime(args.interval)
    else:
        result = engine.run_cycle()
        print("\n" + "="*50)
        print("TRADING CYCLE RESULT")
        print("="*50)
        print(f"Symbol: {result['symbol']}")
        print(f"Close: ₹{result['close']:.2f}")
        print(f"\nIndicators:")
        for k, v in result['indicators'].items():
            print(f"  {k}: {v}")
        print(f"\nSignal: {result['signal']}")
        print(f"Scores: {result['scores']}")
        print("="*50)


if __name__ == '__main__':
    main()