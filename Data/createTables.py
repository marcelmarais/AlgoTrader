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
