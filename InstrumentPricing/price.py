from datetime import date as dt
from datetime import datetime
import math

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
            latest = latest['open']
            
            for i in latest:
                if math.isnan(i):
                    pass
                else:
                    latest = i
                    break
        except:
            print("Could not fetch latest price. (Markets are probably closed)")
            latest = math.nan
        return latest

    def get_company_name(self):
        company_name = self.stock_object.get_company_name()
        return company_name

    def get_stock_logo(self):
        logo = self.stock_object.get_logo()['url']
        return logo


if __name__ == "__main__":
    test = price_data('14-05-2019', ticker="GOOGL")
    print(test.get_stock_logo())
