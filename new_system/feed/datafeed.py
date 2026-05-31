"""
Data Feed Module - Yahoo Finance + Shoonya
"""
import yfinance as yf
import numpy as np
from typing import Optional, Dict, List
from datetime import datetime, timedelta

class DataFeed:
    """Unified data feed using yfinance for prices"""
    
    # NSE index tokens for Shoonya
    INDEX_TOKENS = {
        'NIFTY': ('NSE', '26000'),
        'BANKNIFTY': ('NSE', '26009'),
        'SENSEX': ('NSE', '26017'),
    }
    
    def __init__(self, broker_api=None):
        self.broker_api = broker_api
    
    def fetch_ohlcv(self, symbol: str, period: str = '5d', interval: str = '5m') -> Optional[Dict]:
        """Fetch OHLCV data from yfinance"""
        try:
            # Handle NSE indices - don't add .NS suffix
            if symbol.startswith('^'):
                ticker = yf.Ticker(symbol)
            else:
                ticker = yf.Ticker(f"{symbol}.NS" if not symbol.endswith('.NS') else symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                return None
                
            return {
                'symbol': symbol,
                'data': df,
                'timestamps': df.index.tolist(),
                'open': df['Open'].values.astype(np.float64),
                'high': df['High'].values.astype(np.float64),
                'low': df['Low'].values.astype(np.float64),
                'close': df['Close'].values.astype(np.float64),
                'volume': df['Volume'].values.astype(np.float64),
            }
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def fetch_live_quote(self, symbol: str) -> Optional[Dict]:
        """Fetch live quote from broker (Shoonya) or yfinance fallback"""
        # Try broker first
        if self.broker_api:
            token = self.INDEX_TOKENS.get(symbol.upper())
            if token:
                exch, tok = token
                quote = self.broker_api.get_quotes(exch, tok)
                if quote and quote.get('stat') == 'Ok':
                    return {
                        'symbol': symbol,
                        'ltp': float(quote.get('lp', 0)),
                        'close': float(quote.get('c', 0)),
                        'timestamp': datetime.now()
                    }
        
        # Fallback to yfinance
        ticker = yf.Ticker(f"{symbol}.NS" if not symbol.endswith('.NS') else symbol)
        info = ticker.info.get('currentPrice') or ticker.info.get('lastPrice')
        if info:
            return {
                'symbol': symbol,
                'ltp': info,
                'close': info,
                'timestamp': datetime.now()
            }
        return None
    
    def get_live_price(self, symbol: str) -> Optional[float]:
        """Get just the current price"""
        quote = self.fetch_live_quote(symbol)
        return quote['ltp'] if quote else None


if __name__ == '__main__':
    # Test
    feed = DataFeed()
    data = feed.fetch_ohlcv('^NSEI', period='1d', interval='5m')
    if data:
        print(f"Fetched {len(data['close'])} candles for {data['symbol']}")
        print(f"Latest close: {data['close'][-1]:.2f}")