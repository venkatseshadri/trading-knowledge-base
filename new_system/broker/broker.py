"""
Broker Module - Shoonya API Integration
"""
import yaml
from typing import Dict, List, Optional
import logging

class BrokerClient:
    """Shoonya broker client using NorenApiPy"""
    
    def __init__(self, cred_path: str = None):
        self.api = None
        self.creds = None
        self.connected = False
        
        if cred_path:
            self.load_credentials(cred_path)
    
    def load_credentials(self, cred_path: str):
        """Load credentials from YAML"""
        from api_helper import NorenApiPy
        
        with open(cred_path, 'r') as f:
            self.creds = yaml.safe_load(f)
        
        self.api = NorenApiPy()
        self.api.set_session(self.creds['UID'], self.creds['Access_token'])
        self.connected = True
        logging.info(f"Connected to Shoonya as {self.creds['UID']}")
    
    def get_quote(self, exchange: str, token: str) -> Optional[Dict]:
        """Get quote for a symbol"""
        if not self.api:
            return None
        return self.api.get_quotes(exchange, token)
    
    def get_positions(self) -> List[Dict]:
        """Get open positions"""
        if not self.api:
            return []
        return self.api.get_positions() or []
    
    def get_limits(self) -> Dict:
        """Get account limits"""
        if not self.api:
            return {}
        return self.api.get_limits() or {}
    
    def get_order_book(self) -> List[Dict]:
        """Get order book"""
        if not self.api:
            return []
        return self.api.get_order_book() or []
    
    def place_order(self, symbol: str, exchange: str, qty: int,
                   product: str = 'I', order_type: str = 'M',
                   price: float = 0, trigger_price: float = 0,
                   side: str = 'BUY', validity: str = 'DAY') -> Optional[Dict]:
        """Place an order"""
        if not self.api:
            return None
        
        # Map side to buy/sell
        buy_or_sell = 'B' if side.upper() == 'BUY' else 'S'
        
        # Get token for symbol (need to add mapping)
        # For now, use a simple approach
        
        try:
            result = self.api.place_order(
                buy_or_sell=buy_or_sell,
                producttype=product,
                exchange=exchange,
                tradingsymbol=symbol,
                quantity=qty,
                price=price,
                ordertype=order_type,
                triggerprice=trigger_price,
                validity=validity
            )
            return result
        except Exception as e:
            logging.error(f"Order placement failed: {e}")
            return None
    
    def get_holdings(self) -> List[Dict]:
        """Get holdings"""
        if not self.api:
            return []
        return self.api.get_holdings() or []
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        if not self.api:
            return False
        try:
            return self.api.cancel_order(order_id)
        except:
            return False
    
    def get_option_chain(self, symbol: str, exchange: str = 'NFO') -> List[Dict]:
        """Get option chain for a symbol"""
        if not self.api:
            return []
        return self.api.get_option_chain(symbol, exchange) or []


# Token mapping for common NSE symbols
NSE_TOKENS = {
    'NIFTY': ('NSE', '26000'),
    'BANKNIFTY': ('NSE', '26009'),
    'NIFTYIT': ('NSE', '26011'),
    'RELIANCE': ('NSE', '2885'),
    'TCS': ('NSE', '1594'),
    'INFY': ('NSE', '1594'),  # Need correct token
    'HDFCBANK': ('NSE', '4963'),
    'SBIN': ('NSE', '3045'),
}


if __name__ == '__main__':
    # Test
    import os
    cred_path = os.path.expanduser('~/python-trader/Shoonya_oAuthAPI-py/cred.yml')
    
    broker = BrokerClient(cred_path)
    if broker.connected:
        limits = broker.get_limits()
        print(f"Turnover limit: {limits.get('turnoverlmt', 'N/A')}")
        
        # Get Nifty quote
        exch, tok = NSE_TOKENS['NIFTY']
        quote = broker.get_quote(exch, tok)
        print(f"NIFTY: {quote}")