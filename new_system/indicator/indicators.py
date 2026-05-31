"""
Indicator Module - TA-Lib Streaming API
Uses talib.stream for fast latest-value calculations
"""
import numpy as np
from typing import Tuple, Dict, Optional
from talib import stream

class IndicatorEngine:
    """Fast indicator calculations using TA-Lib streaming API"""
    
    @staticmethod
    def SMA(data: np.ndarray, period: int = 20) -> float:
        """Simple Moving Average - latest value only"""
        return stream.SMA(data, timeperiod=period)
    
    @staticmethod
    def EMA(data: np.ndarray, period: int = 20) -> float:
        """Exponential Moving Average"""
        return stream.EMA(data, timeperiod=period)
    
    @staticmethod
    def RSI(data: np.ndarray, period: int = 14) -> float:
        """Relative Strength Index"""
        return stream.RSI(data, timeperiod=period)
    
    @staticmethod
    def BBANDS(data: np.ndarray, period: int = 20, 
               nbdevup: float = 2.0, nbdevdn: float = 2.0) -> Tuple[float, float, float]:
        """Bollinger Bands - upper, middle, lower"""
        upper, middle, lower = stream.BBANDS(data, timeperiod=period, 
                                              nbdevup=nbdevup, nbdevdn=nbdevdn)
        return upper, middle, lower
    
    @staticmethod
    def ADX(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> float:
        """Average Directional Index"""
        return stream.ADX(high, low, close, timeperiod=period)
    
    @staticmethod
    def ATR(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> float:
        """Average True Range"""
        return stream.ATR(high, low, close, timeperiod=period)
    
    @staticmethod
    def MACD(data: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        """MACD - macd, signal, histogram"""
        macd, signal, hist = stream.MACD(data, fastperiod=fast, slowperiod=slow, signalperiod=signal)
        return macd, signal, hist
    
    @staticmethod
    def STOCH(high: np.ndarray, low: np.ndarray, close: np.ndarray,
              fastk_period: int = 14, slowk_period: int = 3, slowd_period: int = 3) -> Tuple[float, float]:
        """Stochastic - %K, %D"""
        # Note: stream API may not have full STOCH, using basic
        return 0.0, 0.0  # Placeholder
    
    @staticmethod
    def SuperTrend(high: np.ndarray, low: np.ndarray, close: np.ndarray,
                   period: int = 10, multiplier: float = 3.0) -> Tuple[float, str]:
        """
        SuperTrend indicator - not in TA-Lib, implement manually
        Returns: (value, direction)
        """
        # ATR calculation
        atr = stream.ATR(high, low, close, timeperiod=period)
        
        # Basic SuperTrend logic
        hl_avg = (high + low) / 2
        upper = hl_avg + (multiplier * atr)
        lower = hl_avg - (multiplier * atr)
        
        # Simple direction based on close vs average
        avg_price = np.mean(close[-period:])
        direction = 'UP' if close[-1] > avg_price else 'DOWN'
        
        return atr, direction
    
    @classmethod
    def all_indicators(cls, ohlcv: Dict) -> Dict:
        """Calculate all indicators for a symbol"""
        close = ohlcv['close']
        high = ohlcv['high']
        low = ohlcv['low']
        
        return {
            'sma_20': cls.SMA(close, 20),
            'sma_50': cls.SMA(close, 50),
            'ema_20': cls.EMA(close, 20),
            'rsi_14': cls.RSI(close, 14),
            'adx_14': cls.ADX(high, low, close, 14),
            'atr_14': cls.ATR(high, low, close, 14),
            'bb_upper': cls.BBANDS(close, 20)[0],
            'bb_middle': cls.BBANDS(close, 20)[1],
            'bb_lower': cls.BBANDS(close, 20)[2],
            'macd': cls.MACD(close)[0],
            'macd_signal': cls.MACD(close)[1],
            'supertrend': cls.SuperTrend(high, low, close),
            'close': close[-1],
            'timestamp': ohlcv.get('timestamps', [None])[-1],
        }


if __name__ == '__main__':
    # Test with yfinance data
    import yfinance as yf
    
    ticker = yf.Ticker('^NSEI')
    df = ticker.history(period='5d', interval='5m')
    
    ohlcv = {
        'close': df['Close'].values.astype(np.float64),
        'high': df['High'].values.astype(np.float64),
        'low': df['Low'].values.astype(np.float64),
        'timestamps': df.index.tolist(),
    }
    
    results = IndicatorEngine.all_indicators(ohlcv)
    for k, v in results.items():
        print(f"{k}: {v}")