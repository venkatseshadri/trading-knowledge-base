Hi Claude, As per our discussion we need to complete Varaha implementation for the 90% hit rate configuration.
Please assume all write permission and file creation permissions. This should be an optimal model as
 we are starting the varaha trading journey with you.

Parallely, we need to create a data capture system which runs from 9:15 AM to 3:30 AM and collects every 1 minute, 
the following 
* NIFTY SPOT price
* NIFTY Futures price 
* Day of execution
* days from weekly expiry
* days from next weekly expiry
* days from monthly expiry
* price of ATM- CE and PE (weekly, next weekly and monthly contracts)
* price of ATM to ATM +5 CE (weekly, next weekly and monthly contracts)
* price of ATM to ATM -5 CE (weekly, next weekly and monthly contracts)
* capture indicators like 5EMA, 20EMA, 50EMA
* SuperTrend, ADX(14), ATR(14)
* india vix
* rsi

Once per day
* open price, yesterday close price

this would helpful in EOD analysis after the market is closed to understand where we could have taken the trade. 
So once we have that information over a period of 7-14 days, then we make the change in the algorithm. 
