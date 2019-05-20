import sqlite3
import traceback

with open('Data/AlgoTrader.db', 'w'): pass

conn = sqlite3.connect('Data/AlgoTrader.db')
c = conn.cursor()
try:
  c.execute('''CREATE TABLE Main
          (
          date           TEXT    PRIMARY KEY NOT NULL,
          open        REAL,
          high     REAL,
          low      REAL,
          close      REAL,
          volume     REAL)
          ''')

  c.execute('''CREATE TABLE Sentiment
          (
          SentimentID INTEGER PRIMARY KEY     AUTOINCREMENT,
          date           TEXT  ,
          sentiment        REAL,
          sentiment_lag        REAL,
          open     REAL,
          close     REAL,
          volume     REAL,
          position     REAL,
          FOREIGN KEY(date) REFERENCES Main(date)
          )
          ''')
  c.execute('''CREATE TABLE MovingAverages
          (
          MovingAverageID INTEGER PRIMARY KEY     AUTOINCREMENT,
          date           TEXT  ,
          open        REAL,
          close      REAL,
          volume     REAL,
          SMA     REAL,
          EMA     REAL,
          MACD     REAL,
          MACDsignal     REAL,
          BollingerLower     REAL,
          BollingerUpper     REAL,
          FOREIGN KEY(date) REFERENCES Main(date)
          )
          ''')
  
  c.execute('''CREATE TABLE Momentum
          (
          MomentumID INTEGER PRIMARY KEY     AUTOINCREMENT,
          date           TEXT  ,
          RSI_14        REAL,
          Stoch_RSI_14      REAL,
          OBV     REAL,
          OBV_20     REAL,
          SOk     REAL,
          SOd_3     REAL,
          TSI_25_13     REAL,
          Ultimate_Osc     REAL,
          ADX_14_14     REAL,
          MFI_14     REAL,
          FOREIGN KEY(date) REFERENCES Main(date)
          )
          ''')

  c.execute('''CREATE TABLE ArticleTitles
          (TitleID INTEGER PRIMARY KEY     AUTOINCREMENT,
          date           TEXT    NOT NULL,
          title            TEXT     NOT NULL,
          sentiment        REAL,
          URL         TEXT,
          FOREIGN KEY(date) REFERENCES Main(date)
          );''')

  print("Tables created successfully");
  conn.commit()
  conn.close()

except:
  traceback.print_exc()
