import datetime
import pickle
import sys
import time
import sqlite3

from datetime import date as dt

import dateutil.relativedelta
import pandas as pd

from InstrumentPricing import price as pr
from SentimentAnalysis.news import news_data

conn = sqlite3.connect('Data/AlgoTrader.db')
c = conn.cursor()

start_time = time.time()

sensitivity = 1.25  # STD multiple

args = len(sys.argv)

if args > 1:
    ticker = sys.argv[1]

    with open("Data/ticker.txt", 'w') as f:
        f.write(ticker)

    if args > 2:
        cache = eval(sys.argv[2])
    else:
        cache = False
else:
    with open("Data/ticker.txt") as f:
        ticker = f.read()

    cache = False

end = datetime.datetime.strptime(str(dt.today()), "%Y-%m-%d")

start = datetime.datetime.strptime(
    str(dt.today() - dateutil.relativedelta.relativedelta(years=1)),
    "%Y-%m-%d")

start_sentiment = datetime.datetime.strptime(
    str(dt.today() - dateutil.relativedelta.relativedelta(months=1)),
    "%Y-%m-%d")

instrument_info = pr.price_data(start, end_date=end, ticker=ticker)


date_generated = [
    start + datetime.timedelta(days=x) for x in range(0, (end - start).days)
]

sentiment_date_generated = [
    start_sentiment + datetime.timedelta(days=x) for x in range(0, (end - start_sentiment).days)
]

dates_list = []
sentiment_dates_list = []

# Dates added here:

for date in date_generated:
    dates_list.append(date.strftime("%m-%d-%Y"))

for date in sentiment_date_generated:
    sentiment_dates_list.append(date.strftime("%m-%d-%Y"))

# Prices added here:

if cache == True:
    prices = pd.read_pickle("Data/price.pkl")

else:
    comp_name = instrument_info.get_company_name()
    print(f"Fetching {comp_name} price data.")
    prices = pd.DataFrame(instrument_info.get_prices())
    prices = prices.reset_index()

    latest_open = instrument_info.get_latest_price()


    prices = prices.append(
            {'date': end, 'open': instrument_info.get_latest_price()}, ignore_index=True)
    
    if latest_open != None:
     print(f"The latest opening price is: ${latest_open}")

    prices.to_pickle("Data/price.pkl")
    c.execute('DELETE FROM Main')
    
    for i in prices.iterrows():
        values = i[1]
        insert_values = (str(values[0]),values[1],values[2],values[3],
                        values[4],values[5])

        c.execute("""INSERT INTO Main
        VALUES(?,?,?,?,?,?)
        """,insert_values)


    with open("Data/company_name.txt", 'w') as f:
        f.write(comp_name)

    print("Done!\n")


# Sentiment and News Titles added here:

senti = []

urls = []
title_dates = []
all_titles = []
title_senti = []

if cache == True:
    news_data = pd.read_pickle("Data/newsData.pickle")
    title_data = pd.read_pickle("Data/titleData.pickle")
   
    print("Data is being loaded from memory.\n")

else:
    print("Fetching news sentiment.")
    tot_results = 0

    for dates in sentiment_dates_list:
        data = news_data(from_date=str(dates))
        senti.append(data.get_avg_sentiment())
        tot_results += data.get_num_results()

        for title in data.get_titles():
            title_dates.append(dates)
            all_titles.append(title)

        for url in data.get_urls():
            urls.append(url)

        for title_sentiment in data.get_sentiment():
            title_senti.append(title_sentiment)

    print(f"{tot_results} results were found.")
    print("Done!\n")

    title_data = pd.DataFrame({
        'Date': title_dates,
        'Titles': all_titles,
        'Sentiment': title_senti,
        'URL': urls
    })

    news_data = pd.DataFrame({
        'Date': sentiment_dates_list,
        'sentiment': senti,
    })

    news_data.to_pickle('Data/newsData.pickle')
    title_data.to_pickle('Data/titleData.pickle')

news_data = news_data.astype({"Date": 'datetime64[ns]'})
title_data = title_data.astype({"Date": 'datetime64[ns]'})


days_to_drop = list(range(0,len(prices)-(len(news_data)-9)))#Num of weekends

prices_to_merge = prices.copy()

print(prices_to_merge.tail())
prices_to_merge = prices_to_merge.drop(days_to_drop, axis = 0)
print(prices_to_merge.head())

combined = pd.merge(
    news_data,
    prices_to_merge[['date', 'close', 'open', 'volume']],
    right_on='date',
    left_on='Date',
    how='right')
combined = combined.drop('Date', axis=1)

# Price deltas added here:

combined['close_delta'] = combined['close'].pct_change()
combined['open_delta'] = combined['open'].pct_change()


# Sentiment lags added here:

combined['sentiment'] = combined['sentiment'].pct_change()
combined['sentiment_lag'] = combined['sentiment'].shift(1)

# Positions added here:


def deter_pos(row,
              sensitivity,
              mean=combined['sentiment_lag'].mean(),
              std=combined['sentiment_lag'].std()):

    position = []

    for i in row:
        i = float(i)
        pos = 'hold'

        if i > mean + (sensitivity * std):
            pos = 'buy'

        if i < mean - (sensitivity * std):
            pos = 'sell'

        position.append(pos)
    return position


combined['positions'] = deter_pos(combined['sentiment_lag'], sensitivity)
combined.to_csv('SentimentData.csv', index=False)

c.execute('DELETE FROM ArticleTitles')
c.execute('DELETE FROM Sentiment')

for i in combined.iterrows():
    values = i[1]
    insert_values = (str(values[1]),values[0],values[7],values[3],
                    values[2],values[4],values[8])

    c.execute("""INSERT INTO Sentiment
    VALUES(NULL,?,?,?,?,?,?,?)
    """,insert_values)

for i in title_data.iterrows():
    values = i[1]
    insert_title_values = (str(values[0]), values[1], values[2], values[3])

    c.execute("""INSERT INTO ArticleTitles 
     VALUES(NULL,?,?,?,?)
     """, insert_title_values)


conn.commit()
conn.close()


end_time = time.time()
time_taken = end_time - start_time

print("Time taken: {:.2f}".format(time_taken))