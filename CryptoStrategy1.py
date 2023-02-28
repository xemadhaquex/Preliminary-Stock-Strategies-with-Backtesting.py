import yfinance as yf
import numpy as np
import pandas as pd
import pandas_ta as ta
from backtesting import Backtest, Strategy #backtesting.py
from backtesting.lib import crossover
from backtesting.test import SMA

from matplotlib import pyplot as plt
import csv


#backtesting.py documentation: https://kernc.github.io/backtesting.py/doc/backtesting/backtesting.html#backtesting.backtesting.Strategy.buy

#Read in crypto data from csv, will probably want a way to get this data streamed in so that you dont have to download a csv every hour

df = pd.read_csv ('Gemini_BTCUSD_1h.csv',names=['unix','date','symbol','Open','High','Low','Close','Volume BTC','Volume USD'])

df = df.iloc[::-1]

hist = df[-36000:] # unix,date,symbol,open,high,low,close,Volume BTC,Volume USD

print(hist.keys())

opens = hist['Open']
closes = hist['Close']

fastMA = ta.sma(closes,9)
midMA = ta.sma(closes,15)
slowMA = ta.sma(closes,24)

plt.plot(closes,color='black')
plt.plot(fastMA,color= 'red')
plt.plot(midMA,color='green')
plt.plot(slowMA,color='blue')

plt.draw()

riskRewardRatio = .5 # =TakeProfit percentage/ StopLoss Percentage
TakeProfit = .02 # percent at which we want the code to take profit, will directly effect Stop loss because of RiskRewardRatio
StopLoss = TakeProfit/riskRewardRatio


#make backtesting.py strategy (going to try backtrader for a bit)

class SmaCross(Strategy):
    

    def init(self): 
        self.close = self.data.Close 
        self.candleNumber = 0
        self.isInTrade = False
        
    def next(self):

        close = self.close[-1]#Get current price in backtest
        
        if fastMA[self.candleNumber] > slowMA[self.candleNumber] and self.trades != None:
            if self.orders:
                for order in self.orders:
                    order.cancel()
            self.buy()
        
        elif fastMA[self.candleNumber] < slowMA[self.candleNumber] and self.trades != None:
            self.sell()
        '''
        if self.trades:# STOP LOSS AND TAKE PROFIT
            if self.trades[-1].pl_pct >= TakeProfit:
                #print(self.trades[-1].pl_pct)
                for trade in self.trades:
                    trade.close()
            elif self.trades[-1].pl_pct <= -TakeProfit/riskRewardRatio:
                #print(self.trades[-1].pl_pct)
                for trade in self.trades:
                    trade.close()
        '''
        
        self.candleNumber+=1

#One-Time backtest with backtrader.py class:

bt = Backtest(hist, SmaCross,
              cash=50000, commission=.0000,
              exclusive_orders=True)
output = bt.run()
bt.plot(plot_width=2450)

print(output)

#plt.show()

