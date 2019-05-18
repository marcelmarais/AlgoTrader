import pandas as pd
import os
import matplotlib.pyplot as plt 
import math

class MA():
  
  def __init__(self,data,window=20):
    self.df = data
    self.window = window

  def sma(self):
    sma = self.df
    sma = sma.rolling(window=self.window).mean()
    return sma

  def ema(self,window=20):
    ema = self.df
    ema = ema.ewm(min_periods = window,span= window).mean()
    return ema

  def ema_MACD(self,data,window):
    ema = pd.DataFrame(data)
    ema = ema.ewm(min_periods = window,span= window).mean()
    return ema

  def MACD(self):
      ema26 = self.ema(window = 26)
      ema12 = self.ema(window = 12)
      MACD = []

      for i in range(14):
          MACD.append(math.nan)
      for i in range(0,len(ema12)-14):
          MACD.append(ema12[i+14]-ema26[i])

      return MACD

  def MACD_signal(self):
      signal = self.ema_MACD(self.MACD(),9)
      signal = signal[0].tolist()
      return signal


if __name__ == "__main__":
  data = pd.read_pickle('price.pkl')['open']
  data = data.drop(len(data)-1)
  ma = MA(data)

  print(ma.MACD())
  print(ma.MACD_Signal())


