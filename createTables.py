import sqlite3

conn = sqlite3.connect('Data/AlgoTrader.db')


c = conn.cursor()

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

c.execute('''CREATE TABLE ArticleTitles
         (TitleID INTEGER PRIMARY KEY     AUTOINCREMENT,
         date           TEXT    NOT NULL,
         title            TEXT     NOT NULL,
         sentiment        REAL,
         URL         TEXT,
         FOREIGN KEY(date) REFERENCES Main(date)
         );''')


# c.execute("""INSERT INTO Main VALUES("2019-04-02",0.1,200,300,0.2,0.3,5000,"buy")""")
# c.execute("""INSERT INTO NewsArticleSentiment VALUES(NULL,"2019-04-02","some title",0.42,"https://google.com")""")
# c.execute("""INSERT INTO NewsArticleSentiment VALUES(NULL,"2019-04-02","fire",0.3242,"https://google.com/oops")""")


print("Tables created successfully");

conn.commit()
conn.close()
