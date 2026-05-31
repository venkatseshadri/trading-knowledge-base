"""
Strategy Module - Trading strategies using indicators
"""
import numpy as np
from typing import Dict, Optional, Tuple
from enum import Enum

class Signal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    NEUTRAL = "NEUTRAL"

class TradingStrategy:
    """Base trading strategy"""
    
    def __init__(self, name: str):
        self.name = name
    
    def evaluate(self, indicators: Dict) -> Signal:
        """Evaluate indicators and return signal"""
        raise NotImplementedError


class SMACrossover(TradingStrategy):
    """SMA Crossover Strategy"""
    
    def __init__(self, fast_period: int = 20, slow_period: int = 50):
        super().__init__("SMA_Crossover")
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def evaluate(self, indicators: Dict) -> Signal:
        sma_fast = indicators.get(f'sma_{self.fast_period}')
        sma_slow = indicators.get(f'sma_{self.slow_period}')
        
        if sma_fast is None or sma_slow is None:
            return Signal.NEUTRAL
        
        # Simple crossover logic
        if sma_fast > sma_slow:
            return Signal.BUY
        elif sma_fast < sma_slow:
            return Signal.SELL
        return Signal.NEUTRAL


class RSIStrategy(TradingStrategy):
    """RSI Overbought/Oversold Strategy"""
    
    def __init__(self, period: int = 14, oversold: float = 30, overbought: float = 70):
        super().__init__("RSI")
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def evaluate(self, indicators: Dict) -> Signal:
        rsi = indicators.get(f'rsi_{self.period}')
        
        if rsi is None:
            return Signal.NEUTRAL
        
        if rsi < self.oversold:
            return Signal.BUY
        elif rsi > self.overbought:
            return Signal.SELL
        return Signal.NEUTRAL


class ADXTrendStrategy(TradingStrategy):
    """ADX Trend Following Strategy"""
    
    def __init__(self, period: int = 14, adx_threshold: float = 25):
        super().__init__("ADX_Trend")
        self.period = period
        self.adx_threshold = adx_threshold
    
    def evaluate(self, indicators: Dict) -> Signal:
        adx = indicators.get(f'adx_{self.period}')
        close = indicators.get('close')
        supertrend = indicators.get('supertrend', (0, 'NEUTRAL'))
        
        if adx is None or close is None:
            return Signal.NEUTRAL
        
        # ADX > 25 = trending, < 25 = ranging
        if adx > self.adx_threshold:
            direction = supertrend[1] if isinstance(supertrend, tuple) else 'NEUTRAL'
            if direction == 'UP':
                return Signal.BUY
            elif direction == 'DOWN':
                return Signal.SELL
        
        return Signal.NEUTRAL


class MultiIndicatorStrategy(TradingStrategy):
    """Combine multiple indicators with weights"""
    
    def __init__(self, weights: Dict[str, float] = None):
        super().__init__("MultiIndicator")
        self.weights = weights or {
            'adx': 0.4,
            'rsi': 0.3,
            'sma': 0.2,
            'bb': 0.1,
        }
        self.strategies = {
            'adx': ADXTrendStrategy(),
            'rsi': RSIStrategy(),
            'sma': SMACrossover(),
            'bb': None,  # BB handled separately
        }
    
    def evaluate(self, indicators: Dict) -> Tuple[Signal, Dict]:
        scores = {'BUY': 0, 'SELL': 0, 'NEUTRAL': 0}
        
        # Evaluate each strategy
        for name, strategy in self.strategies.items():
            if strategy is None:
                continue
            signal = strategy.evaluate(indicators)
            weight = self.weights.get(name, 0)
            
            if signal != Signal.NEUTRAL:
                scores[signal.value] += weight * 100
        
        # Calculate signal
        total = scores['BUY'] + scores['SELL']
        
        if total == 0:
            return Signal.NEUTRAL, scores
        
        buy_ratio = scores['BUY'] / total
        
        if buy_ratio > 0.6:
            return Signal.BUY, scores
        elif buy_ratio < 0.4:
            return Signal.SELL, scores
        
        return Signal.NEUTRAL, scores


# Strategy factory
def get_strategy(strategy_name: str, **params) -> TradingStrategy:
    """Get strategy by name"""
    strategies = {
        'sma_crossover': SMACrossover,
        'rsi': RSIStrategy,
        'adx_trend': ADXTrendStrategy,
        'multi': MultiIndicatorStrategy,
    }
    
    strategy_class = strategies.get(strategy_name.lower())
    if strategy_class:
        return strategy_class(**params)
    
    raise ValueError(f"Unknown strategy: {strategy_name}")


if __name__ == '__main__':
    # Test
    test_indicators = {
        'sma_20': 24350.0,
        'sma_50': 24300.0,
        'rsi_14': 65.0,
        'adx_14': 30.0,
        'close': 24340.0,
        'supertrend': (150, 'UP'),
    }
    
    strategy = MultiIndicatorStrategy()
    signal, scores = strategy.evaluate(test_indicators)
    print(f"Signal: {signal.value}, Scores: {scores}")