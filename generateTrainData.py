import datetime
import pickle
import sqlite3
import sys
import time
import argparse
import json
import os
from datetime import date as dt

import dateutil.relativedelta
import pandas as pd

from InstrumentPricing import price as pr
from SentimentAnalysis.news import news_data

start_time = time.time()

stock_data = {}

parser = argparse.ArgumentParser()

parser.add_argument("-t", "--ticker",
                    help="Specify the ticker symbol.")

parser.add_argument("-c", "--cache", action="store_true",
                    help="Indicate if you want to use cached data.")

parser.add_argument("-s", "--sensitivity", type=float,
                    help="Sets the buy/sell sensitivity in\
                         STD multiples.")

cl_args = parser.parse_args()

cache = cl_args.cache

if not cache: exec(open("Data/createTables.py").read())

try:
    with open("Data/stock_data.json") as f:
        prev_stock_data = json.load(f)
except:
    if cache:
        print("""
            It looks like you are trying to run the program
            for the first time with the cache option - don't do this
            """)
        exit()
    else:
        pass

if cl_args.ticker:

    if cache:
        print("Ticker symbol is ignored when cache is enabled.")
        ticker = prev_stock_data['ticker']

    else:
        ticker = cl_args.ticker
        stock_data['ticker'] = ticker
else:
    ticker = prev_stock_data['ticker']


if cl_args.sensitivity:
    sensitivity = cl_args.sensitivity  # STD multiple
else:
    sensitivity = 1

conn = sqlite3.connect('Data/AlgoTrader.db')
c = conn.cursor()

end = datetime.datetime.strptime(str(dt.today()), "%Y-%m-%d")

start = datetime.datetime.strptime(
    str(dt.today() - dateutil.relativedelta.relativedelta(years=1)),
    "%Y-%m-%d")

instrument_info = pr.price_data(start, end_date=end, ticker=ticker)


dates_generated = [
    start + datetime.timedelta(days=x) for x in range(0, (end - start).days)
]

dates_list = []

# Dates added here:

for date in dates_generated:
    dates_list.append(date.strftime("%m-%d-%Y"))

sentiment_dates_list = dates_generated[::-1][:30]

# Prices added here:

if cache:
    comp_name = prev_stock_data['FullName']
    print(f"Loading data for: {comp_name}")
    prices = pd.read_pickle("Data/price.pkl")

else:
    comp_name = instrument_info.get_company_name()
    logo = instrument_info.get_stock_logo()

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
        insert_values = (str(values[0]), values[1], values[2], values[3],
                         values[4], values[5])

        c.execute("""INSERT INTO Main
        VALUES(?,?,?,?,?,?)
        """, insert_values)

    stock_data['FullName'] = comp_name
    stock_data['Logo'] = logo

    print("Done!\n")

# Sentiment and News Titles added here:

senti = []

urls = []
title_dates = []
all_titles = []
title_senti = []

if cache:
    news_data = pd.read_pickle("Data/newsData.pkl")
    title_data = pd.read_pickle("Data/titleData.pkl")

    print("Data is being loaded from memory.\n")

else:
    print("Fetching news sentiment.")
    tot_results = 0

    for dates in sentiment_dates_list[::-1]:
        data = news_data(comp_name,from_date=str(dates))
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

    news_data.to_pickle('Data/newsData.pkl')
    title_data.to_pickle('Data/titleData.pkl')

news_data = news_data.astype({"Date": 'datetime64[ns]'})
title_data = title_data.astype({"Date": 'datetime64[ns]'})

prices_to_merge = prices.copy()

combined = pd.merge(
    news_data,
    prices_to_merge[['date', 'close', 'open', 'volume']],
    right_on='date',
    left_on='Date',
    how='left')

combined = combined.drop('date', axis=1)

# Price deltas added here:

combined['close_delta'] = combined['close'].pct_change()
combined['open_delta'] = combined['open'].pct_change()


# Sentiment lags added here:

combined['sentiment_lag'] = combined['sentiment'].shift(1)
# combined['sentiment_delta'] = combined['sentiment'].pct_change()
# combined['sentiment_delta_lag'] = combined['sentiment_delta'].shift(1)
# print(combined.head())
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

c.execute('DELETE FROM ArticleTitles')
c.execute('DELETE FROM Sentiment')

for i in combined.iterrows():
    values = i[1]

    insert_values = (str(values[0]), values[1], values[7], values[3],
                     values[2], values[4], values[8])

    c.execute("""INSERT INTO Sentiment
    VALUES(NULL,?,?,?,?,?,?,?)
    """, insert_values)

for i in title_data.iterrows():
    values = i[1]
    insert_title_values = (str(values[0]), values[1], values[2], values[3])

    c.execute("""INSERT INTO ArticleTitles 
     VALUES(NULL,?,?,?,?)
     """, insert_title_values)

conn.commit()
conn.close()

if not cache:
    with open("Data/stock_data.json", 'w') as f:
        json.dump(stock_data, f)

end_time = time.time()
time_taken = end_time - start_time

print("Time taken: {:.2f}".format(time_taken))
