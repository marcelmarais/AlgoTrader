import pandas as pd
import matplotlib.pyplot as plt 
import math
from statistics import mean

class Momentum():
    def __init__(self,data):
        self.df = data
    def RSI(self):
        data = self.df['open']
        data = data.tolist()
        RSI = []
        for i in range(14):
            RSI.append(math.nan)
        for i in range(0,len(data)-14):
            up = []
            down = []    
            x = pd.DataFrame(data[i:i+15]).diff()
            
            for j in x[0]:
                if j >=0:
                    up.append(j)
                else: down.append(abs(j))
            up = mean(up)         
            down = mean(down[1::])
            RS = up/down #Relative strength
            RSI.append(100-100/(1+RS))                  
        return RSI

    def OBV(self):
        data = self.df
        volume = data['volume']
        open = data['open']
        close = data['close']  
        OBV = [volume[0]]            
        for i in range(1,len(volume)):
            if close[i-1] < close[i]:
                OBV.append(OBV[i-1]+volume[i]) # Change is positive if it was an up-day
            elif close[i-1] > close[i]:
                OBV.append((OBV[i-1]-volume[i])) # Change is negative if it was an down-day         
        return OBV
    
    def DOBV(self):
        DOBV = self.OBV()
        DOBV = pd.DataFrame(DOBV)
        DOBV = DOBV.pct_change()
        return DOBV

    def Stochastic_Oscillator(self): #maybe probably doesn't work
        high = self.df['high']
        high = high.tolist()
        low = self.df['low']
        low = low.tolist()
        close = self.df['close']
        close = close.tolist()
        close =close        
        SO = []
        for i in range(14):
            SO.append(math.nan)
        for i in range(0,len(high)-14):
            highest = max(high[i:i+15])
            lowest = min(low[i:i+15])
            cl = close[i] 
            SO.append(((cl-lowest)/(highest-lowest))*100)
        return SO    

    def SMA_3_SO(self): # 3 day simple moving average of Stochastic Oscillator
        SMA3 = pd.Series(self.Stochastic_Oscillator()).rolling(window=3).mean()        
        SMA3 = SMA3.tolist()       
        return SMA3       

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
  plt.plot(mo.df['date'],mo.df['open'])  
 
  plt.plot(mo.df['date'],mo.Stoch_RSI())  

  plt.show()


  
  