import pandas as pd
import matplotlib.pyplot as plt 
import math
from statistics import mean

class Momentum():
    def __init__(self,data):
        self.df = data
        self.output = pd.DataFrame(self.df['date'])

    
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
        self.output = self.output.join(RSI)
        
        return RSI
    

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
        OBV = pd.Series(OBV, name = 'OBV')
        self.output = self.output.join(OBV)
        col_name = 'OBV_' + str(n)
        OBV_ma = pd.Series(OBV.rolling(n, min_periods=n).mean(), name=col_name)
        self.output = self.output.join(OBV_ma)

        return OBV


    def stochastic_oscillator_k(self):
        """Calculate stochastic oscillator %K for given data.
        
        :param df: pandas.DataFrame
        :return: pandas.DataFrame
        """
        df = self.df
        
        SOk = pd.Series((df['close'] - df['low']) / (df['high'] - df['low']), name='SOk')
        self.output = self.output.join(SOk)
        return SOk   

    def stochastic_oscillator_d(self, n=3):
        """Calculate stochastic oscillator %D for given data.
        :param df: pandas.DataFrame
        :param n: 
        :return: pandas.DataFrame
        """
        df = self.df
        
        SOk = pd.Series((df['close'] - df['low']) / (df['high'] - df['low']), name='SOk')
        SOd = pd.Series(SOk.ewm(span=n, min_periods=n).mean(), name='SOd_' + str(n))
        self.output = self.output.join(SOd)
        
        return SOd
    
    
    def Stoch_RSI(self,n=14):
        RSI = self.RSI()
        StochRSI = []
        for i in range(n):
            StochRSI.append(math.nan)
        for i in range(0,len(RSI)-n):
            highest = max(RSI[i:i+n+1])
            lowest = min(RSI[i:i+n+1])
            val = RSI[i]
            StochRSI.append((val-lowest)/(highest-lowest))
        StochRSI = pd.Series(StochRSI, name = 'Stoch_RSI_' + str(n))   

        self.output = self.output.join(StochRSI)
        return StochRSI    

    def true_strength_index(self, r = 25, s = 13):
        df = self.df

        M = pd.Series(df['close'].diff(1))
        aM = abs(M)
        EMA1 = pd.Series(M.ewm(span=r, min_periods=r).mean())
        aEMA1 = pd.Series(aM.ewm(span=r, min_periods=r).mean())
        EMA2 = pd.Series(EMA1.ewm(span=s, min_periods=s).mean())
        aEMA2 = pd.Series(aEMA1.ewm(span=s, min_periods=s).mean())
        TSI = pd.Series(EMA2 / aEMA2, name='TSI_' + str(r) + '_' + str(s))
        self.output = self.output.join(TSI)
        return TSI
    

    def ultimate_oscillator(self):
        """Calculate Ultimate Oscillator for given data.
        
        :param df: pandas.DataFrame
        :return: pandas.DataFrame
        """
        df = self.df
        i = 0
        TR_l = [0]
        BP_l = [0]
        while i < df.index[-1]:
            TR = max(df.loc[i + 1, 'high'], df.loc[i, 'close']) - min(df.loc[i + 1, 'low'], df.loc[i, 'close'])
            TR_l.append(TR)
            BP = df.loc[i + 1, 'close'] - min(df.loc[i + 1, 'low'], df.loc[i, 'close'])
            BP_l.append(BP)
            i = i + 1
        UltO = pd.Series((4 * pd.Series(BP_l).rolling(7).sum() / pd.Series(TR_l).rolling(7).sum()) + (
                    2 * pd.Series(BP_l).rolling(14).sum() / pd.Series(TR_l).rolling(14).sum()) + (
                                    pd.Series(BP_l).rolling(28).sum() / pd.Series(TR_l).rolling(28).sum()),
                        name='Ultimate_Osc')
        self.output = self.output.join(UltO)
        return UltO

    def average_directional_movement_index(self, n=14, n_ADX=14):
        """Calculate the Average Directional Movement Index for given data.
        
        :param df: pandas.DataFrame
        :param n: 
        :param n_ADX: 
        :return: pandas.DataFrame
        """
        df = self.df
        i = 0
        UpI = []
        DoI = []
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
        i = 0
        TR_l = [0]
        while i < df.index[-1]:
            TR = max(df.loc[i + 1, 'high'], df.loc[i, 'close']) - min(df.loc[i + 1, 'low'], df.loc[i, 'close'])
            TR_l.append(TR)
            i = i + 1
        TR_s = pd.Series(TR_l)
        ATR = pd.Series(TR_s.ewm(span=n, min_periods=n).mean())
        UpI = pd.Series(UpI)
        DoI = pd.Series(DoI)
        PosDI = pd.Series(UpI.ewm(span=n, min_periods=n).mean() / ATR)
        NegDI = pd.Series(DoI.ewm(span=n, min_periods=n).mean() / ATR)
        ADX = pd.Series((abs(PosDI - NegDI) / (PosDI + NegDI)).ewm(span=n_ADX, min_periods=n_ADX).mean(),
                        name='ADX_' + str(n) + '_' + str(n_ADX))
        self.output = self.output.join(ADX)
        return ADX

    def money_flow_index(self,n = 14):
        """Calculate Money Flow Index and Ratio for given data.
        
        :param df: pandas.DataFrame
        :param n: 
        :return: pandas.DataFrame
        """
        df = self.df
        
        PP = (df['high'] + df['low'] + df['close']) / 3
        i = 0
        PosMF = [0]
        while i < df.index[-1]:
            if PP[i + 1] > PP[i]:
                PosMF.append(PP[i + 1] * df.loc[i + 1, 'volume'])
            else:
                PosMF.append(0)
            i = i + 1
        PosMF = pd.Series(PosMF)
        TotMF = PP * df['volume']
        MFR = pd.Series(PosMF / TotMF)
        MFI = pd.Series(MFR.rolling(n, min_periods=n).mean(), name='MFI_' + str(n))

        self.output = self.output.join(MFI)
        return MFI


    def call_all(self):
        self.Stoch_RSI()
        self.OBV()
        self.stochastic_oscillator_k()
        self.stochastic_oscillator_d()
        self.true_strength_index()
        self.ultimate_oscillator()
        self.average_directional_movement_index()
        self.money_flow_index()

        return self.output


if __name__ == "__main__":
    pass
#   data = pd.read_pickle('')
#   data = data.drop(len(data)-1)
#   mo = Momentum(data)
  
#   print(mo.call_all())
  

  #plt.show()

# https://github.com/Crypto-toolbox/pandas-technical-indicators/blob/master/technical_indicators.py