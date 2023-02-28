import yfinance as yf
import numpy as np
import pandas as pd
from backtesting import Backtest, Strategy #backtesting.py
from backtesting.lib import crossover
from backtesting.test import SMA


#backtesting.py documentation: https://kernc.github.io/backtesting.py/doc/backtesting/backtesting.html#backtesting.backtesting.Strategy.buy


#Define ticker for yahoo finance API
ticker = yf.Ticker("SPY")

# get stock info
ticker.info

# get historical market data, 1993 to now of daily data
hist = ticker.history(period="max")
hist = hist[-1200:] #just the last 5000 bars

#we save opens and closes
opens = hist['Open'][0:]
closes = hist['Close'][0:]

#print(hist)
#print(closes)

riskRewardRatio = 2 # =TakeProfit percentage/ StopLoss Percentage
TakeProfit = .1 # percent at which we want the code to take profit, will directly effect Stop loss because of RiskRewardRatio
StopLoss = TakeProfit/riskRewardRatio

n1 = 9 
n2 = 15

#make backtesting.py strategy
class SmaCross(Strategy):

    def init(self):
        close = self.data.Close 
        self.close = self.data.Close 
        self.sma1 = self.I(SMA, close, n1)
        self.sma2 = self.I(SMA, close, n2)
        self.pos = 0
        self.halfClosed = False
        self.prevOrder = None

    def next(self):

        price = self.close[-1]  #Get current price in backtest

        ''' #take profit and stop loss manually

        if self.position.pl_pct != 0:
            print(self.position.pl_pct)
        
        if self.position.pl_pct <= -1*(TakeProfit/riskRewardRatio): #do stop loss here
            self.position.close(1)
            self.pos = 0
            self.halfClosed = False
            print('StopLoss')

        if self.position.pl_pct >= TakeProfit and self.halfClosed == False: #if you exceed your take profit mark then take half profit
            self.position.close(1)
            #self.halfClosed = True
            self.pos = 0
            print('TakeProfit1')
        
        if self.position.pl_pct <= TakeProfit and self.halfClosed == True: #if you previously took half profit and are now under the TP mark, take the rest profit
            self.position.close(1)
            self.pos = 0
            self.halfClosed = False
            print('TakeProfit2')
        '''
        
        if self.trades:
            #print(self.trades[-1].pl_pct)
            if self.trades[-1].pl_pct >= TakeProfit:
                print(self.trades[-1].pl_pct)
                for trade in self.trades:
                    trade.close()
            elif self.trades[-1].pl_pct <= -TakeProfit/riskRewardRatio:
                print(self.trades[-1].pl_pct)
                for trade in self.trades:
                    trade.close()
        
        if crossover(self.sma1, self.sma2): #enter trade if crossover, 
            #self.position.close(1)
            #self.pos = 0
            #self.halfClosed = False
            
            for order in self.orders:
                order.cancel()

            sz = self.equity//price
            self.buy()
            #self.buy(tp=(TakeProfit+1)*price,sl=(1-(TakeProfit/riskRewardRatio))*price, size= sz) #size= sz, #need to start specifying order size and stuff like that when we buy and sell, limit = price-(price/100)
            self.pos = 1

        elif crossover(self.sma2, self.sma1): # #enter trade if crossover 
            #self.position.close(1)
            #self.pos = 0
            #self.halfClosed = False

            for order in self.orders:
                order.cancel()
            
            sz = self.equity//price
            self.sell()
            #self.sell(tp = (1-TakeProfit)*price, sl = price*((TakeProfit/riskRewardRatio)+1), size=sz) #size= sz, limit = price-(price/100)  stop=price,
            self.pos = -1
        

#One-Time backtest:

bt = Backtest(hist, SmaCross,
              cash=50000, commission=.0000,
              exclusive_orders=True)
output = bt.run()
bt.plot(plot_width=2450)

#print(output.trades)
#print(output)