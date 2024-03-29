import json
import os
import requests
import pandas as pd
from textblob import TextBlob
from datetime import date as dt
from datetime import timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import statistics

class news_data():
    def __init__(self, stock_name,from_date=str(dt.today())):

        with open('Data/apiKeys.txt') as f:
            api_key = f.readlines()

        api_key = str(api_key[1])

        key_words = stock_name + ' OR manufacturing'
        key_words = '''yield curve OR core inflation OR manufacturing OR stock valuation'''

        url = ('https://newsapi.org/v2/everything?'
               'pageSize=100&q=' + key_words + '&from=' + from_date + 
               '&to=' + from_date + '&apiKey=' + api_key)

        response = requests.get(url)
        data = response.json()

        try:
            self.num_results = data['totalResults']
        except:
            print(data["status"])
            print(data["code"])
            print(data["message"])
            exit()

        self.raw = data['articles']
        self.title = []
        self.url = []
        self.content = []
        self.date = []

        for i in self.raw:

            title = i['title'].replace(",", "")
            title = title.replace("'", "")
            title = title.replace('"', "")
            self.title.append(title)

            link = i['url']

            if len(link) != 0:
                self.url.append(link)
            else:
                self.url.append("No URL for this article.")

            self.content.append(i['content'])
            self.date.append(i['publishedAt'])

        self.articles = dict(zip(self.title, self.content))
    
    def get_titles(self):
        return self.title
    
    def get_urls(self):
        return self.url

    def sentiment_analyzer_scores(self):
            analyser = SentimentIntensityAnalyzer()

            scores = []
            for i in self.content:
                if i != None:
                    scores.append(analyser.polarity_scores(i)['compound'])
            
            print(statistics.mean(scores))

    def get_sentiment(self):
        self.sentiment_list = []

        for i in range(0, len(self.title)):
            try:
                analysis = TextBlob(self.content[i])
                # print(self.date[i])
                self.sentiment_list.append(analysis.sentiment.polarity)
            except:
                self.sentiment_list.append(0)
        
        if len(self.sentiment_list) == 0:
            self.sentiment_list.append(0)

        return self.sentiment_list

    def get_avg_sentiment(self):
        self.sentiment_list = []

        for i in range(0, len(self.content)):
            try:
                analysis = TextBlob(self.content[i])
                self.sentiment_list.append(analysis.sentiment.polarity)
            except:
                pass

        cnt = 0
        tot = 0

        for i in self.sentiment_list:
            if i != 0:
                cnt += i
                tot += 1
        try:
            avg = cnt / tot
        except:
            avg = 0

        return avg

    def get_num_results(self):
        return self.num_results