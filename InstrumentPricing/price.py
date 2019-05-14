from datetime import date as dt
from datetime import datetime

import pandas as pd
from iexfinance.stocks import (
    Stock, get_historical_data, get_historical_intraday)


# https://cloud.iexapis.com/ref-data/jse/npn
class price_data():
    def __init__(self, start_date, end_date=str(dt.today()), ticker='SPY'):
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.ticker = ticker
        self.stock_object = Stock(ticker)

    def get_prices(self):
        data = get_historical_data(
            self.ticker,
            start=self.start_date,
            end=self.end_date,
            output_format='pandas')
        return data

    def get_latest_price(self):
        try:
            latest = get_historical_intraday(self.ticker, output_format='pandas')
            latest = latest['open']['0']
        except:
            print("Could not fetch latest price. (Markets are probably closed)")
            latest = 0
        return latest

    def get_company_name(self):
        company_name = self.stock_object.get_company_name()
        return company_name


if __name__ == "__main__":
    test = price_data('02-04-2019', ticker="DIA")
    print(test.get_latest_price())
