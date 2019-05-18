import pandas as pd
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

  def Bollinger_Up(self):
    SMA = self.sma()
    STD = self.df
    STD = STD.rolling(window=self.window).std()

    Bollinger_Upper = []

    for i in range(0,len(SMA)):
      Bollinger_Upper.append(SMA[i]+2*STD[i])

    return Bollinger_Upper  

  def Bollinger_Lo(self):
    SMA = self.sma()
    STD = self.df
    STD = STD.rolling(window=self.window).std()

    Bollinger_lower = []

    for i in range(0,len(SMA)):
      Bollinger_lower.append(SMA[i]-2*STD[i])

    return Bollinger_lower  

if __name__ == "__main__":
  data = pd.read_pickle('price.pkl')
  data = data.drop(len(data)-1)
  ma = MA(data['open'])

  plt.plot(data['date'],ma.Bollinger_Hi())
  plt.plot(data['date'],ma.Bollinger_Lo())
  plt.plot(data['date'],ma.sma())
  plt.plot(data['date'],data['open'])
  plt.show()


