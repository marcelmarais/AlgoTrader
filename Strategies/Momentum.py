import pandas as pd
import matplotlib.pyplot as plt 
import math
from statistics import mean

class Momentum():
    def __init__(self,data):
        self.df = data

    def RSI(self,n=14):
        """Calculate Relative Strength Index(RSI) for given data.
        
        :param df: pandas.DataFrame
        :param n: 
        :return: pandas.DataFrame
        """
        i = 0
        UpI = [0]
        DoI = [0]
        df = self.df

        while i + 1 <= df.index[-1]:
            UpMove = df.loc[i + 1, 'high'] - df.loc[i, 'high']
            DoMove = df.loc[i, 'low'] - df.loc[i + 1, 'low']

            if UpMove > DoMove and UpMove > 0:
                UpD = UpMove
            else:
                UpD = 0
            UpI.append(UpD)
            if DoMove > UpMove and DoMove > 0:
                DoD = DoMove
            else:
                DoD = 0
            DoI.append(DoD)
            i = i + 1

        UpI = pd.Series(UpI)
        DoI = pd.Series(DoI)
        PosDI = pd.Series(UpI.ewm(span=n, min_periods=n).mean())
        NegDI = pd.Series(DoI.ewm(span=n, min_periods=n).mean())

        col_name = 'RSI_' + str(n)
        RSI = pd.Series(PosDI / (PosDI + NegDI), name=col_name)
        df = df.join(RSI)
        
        return df[col_name]


    def OBV(self,n=20):
        """Calculate On-Balance Volume for given data.
        
        :param df: pandas.DataFrame
        :param n: 
        :return: pandas.DataFrame
        """
        df = self.df
        i = 0
        OBV = [0]
        while i < df.index[-1]:
            if df.loc[i + 1, 'close'] - df.loc[i, 'close'] > 0:
                OBV.append(df.loc[i + 1, 'volume'])
            if df.loc[i + 1, 'close'] - df.loc[i, 'close'] == 0:
                OBV.append(0)
            if df.loc[i + 1, 'close'] - df.loc[i, 'close'] < 0:
                OBV.append(-df.loc[i + 1, 'volume'])
            i = i + 1
        OBV = pd.Series(OBV)
        col_name = 'OBV_' + str(n)
        OBV_ma = pd.Series(OBV.rolling(n, min_periods=n).mean(), name=col_name)
        df = df.join(OBV_ma)

        return OBV

    
    def DOBV(self):
        DOBV = self.OBV()
        DOBV = pd.DataFrame(DOBV)
        DOBV = DOBV.pct_change()
        return DOBV

    def stochastic_oscillator_k(self):
        """Calculate stochastic oscillator %K for given data.
        
        :param df: pandas.DataFrame
        :return: pandas.DataFrame
        """
        df = self.df
        
        SOk = pd.Series((df['Close'] - df['Low']) / (df['High'] - df['Low']), name='SO%k')
        df = df.join(SOk)
        return df    

    def stochastic_oscillator_d(self, n=3):
        """Calculate stochastic oscillator %D for given data.
        :param df: pandas.DataFrame
        :param n: 
        :return: pandas.DataFrame
        """
        df = self.df
        
        SOk = pd.Series((df['close'] - df['low']) / (df['high'] - df['low']), name='SO%k')
        SOd = pd.Series(SOk.ewm(span=n, min_periods=n).mean(), name='SO%d_' + str(n))
        df = df.join(SOd)
        
        return df
    
    
    def Stoch_RSI(self):
        RSI = self.RSI()
        StochRSI = []
        for i in range(14):
            StochRSI.append(math.nan)
        for i in range(0,len(RSI)-14):
            highest = max(RSI[i:i+15])
            lowest = min(RSI[i:i+15])
            val = RSI[i]
            StochRSI.append((val-lowest)/(highest-lowest))
            
        return StochRSI    




if __name__ == "__main__":

  data = pd.read_pickle('price.pkl')
  data = data.drop(len(data)-1)
  mo = Momentum(data)
  #plt.plot(mo.df['date'],mo.df['open'])  

  mo.RSI()

  #print(mo.relative_strength_index(14))  


  #plt.show()

# https://github.com/Crypto-toolbox/pandas-technical-indicators/blob/master/technical_indicators.py