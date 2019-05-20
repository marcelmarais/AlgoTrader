import pandas as pd
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
    bollinger_upper = []

    STD = self.df.rolling(window=self.window).std()

    for i in zip(self.sma(),STD):
      bollinger_upper.append(i[0]+2*i[1])

    return bollinger_upper  

  def Bollinger_Lo(self):
    bollinger_lower = []

    STD = self.df.rolling(window=self.window).std()

    for i in zip(self.sma(),STD):
      bollinger_lower.append(i[0]-2*i[1])

    return bollinger_lower  

if __name__ == "__main__":
  pass

