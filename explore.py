import json
import math
import pickle
import sqlite3
import traceback
from datetime import date as dt
from datetime import datetime, timedelta

import dash
import dash_core_components as dcc
import dash_html_components as html
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from numpy import array

try:
    with open("Data/stock_data.json") as f:
        stock_data = json.load(f)
except:
    if cache:
        print("""
            It looks like you are trying to run the program
            without generating data first.
            """)
        exit()
    else:
        pass

# All SQL queries happen here:

conn = sqlite3.connect('Data/AlgoTrader.db')

article_query = "SELECT strftime('%Y-%m-%d', date) AS date,sentiment,URL,title FROM ArticleTitles ORDER BY sentiment DESC;"
sentiment_query = "SELECT strftime('%Y-%m-%d', date) AS date,open,close,sentiment,position  FROM Sentiment;"
main_query = "SELECT strftime('%Y-%m-%d', date) AS date,open,volume  FROM Main;"

article_title_data = pd.read_sql_query(article_query, conn)
main_price_data = pd.read_sql_query(main_query, conn)
sentiment_data = pd.read_sql_query(sentiment_query,conn)

conn.commit()
conn.close()

sentiment_data = sentiment_data.dropna(subset=['open'])
main_price_data = main_price_data.dropna(subset=['volume'])

sell_x = []
sell_y = []
buy_x = []
buy_y = []
mvs = []

graph_title = stock_data['FullName']


# Appends buy/sell/hold into separate lists. (PLEASE MAKE THIS BETTER)
def plot_pos(leverage):

    x_pos = []
    y_pos = []

    bought = False
    sold = False

    pos_value = 0
    movement = 0

    for index, row in sentiment_data.iterrows():

        position = row['position']
        price = row['open']

        if position != "hold":

            if position == "sell":
                sell_x.append(row['date'])
                sell_y.append(price)

                if sold == True:
                    pos_value = price

                sold = True

                if bought == True:
                    movement = ((1-(pos_value/price)) * 100 * leverage)
                    mvs.append(movement)
                    bought = False
                    sold = False
                    pos_value = 0

                else:
                    pos_value = price

            if position == "buy":
                buy_x.append(row['date'])
                buy_y.append(price)

                if bought == True:
                    pos_value = price

                bought = True

                if sold == True:
                    movement = -((1-(pos_value/price)) * 100 * leverage)
                    mvs.append(movement)
                    sold = False
                    bought = False
                    pos_value = 0

                else:
                    pos_value = price

    return [list(x_pos), list(y_pos)]


senti = sentiment_data['sentiment']

open_price = sentiment_data['open']
close_price = sentiment_data['close']

date = sentiment_data['date']
dates = []

main_dates = main_price_data['date']
full_dates = []

for i in date:
    dates.append(datetime.strptime(i, "%Y-%m-%d"))

for i in main_dates:
    full_dates.append(datetime.strptime(i, "%Y-%m-%d"))

# plt.plot(dates,close,label='Close')

pos_plt = plot_pos(1)

trades = ""

for i in reversed(mvs):
    trades += str(round(i, 2)) + "% |\t"


def create_plot(y_data, x_data=dates):
    standard_plot = go.Scatter(
        x=x_data,
        y=y_data,

        mode='lines',
        name='Open',
    )

    return standard_plot


main_price_plot = create_plot(main_price_data['open'], full_dates)
open_price_plot = create_plot(open_price)
close_price_plot = create_plot(close_price)

buy_annotations = go.Scatter(
    x=buy_x,
    y=buy_y,
    mode='markers+text',
    name='Buy',
    text="buy",
    textposition='middle right'
)

sell_annotations = go.Scatter(
    x=sell_x,
    y=sell_y,
    mode='markers+text',
    name='Sell',
    text="sell",
    textposition='middle right'
)

app = dash.Dash(__name__, static_folder='assets')

app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

app.layout = html.Div(children=[

    html.Div(style={'display':'flex','flex-direction':'row','flex-wrap':'nowrap','position':'relative','justify-content':'flex-start'},children =[
    
    html.Div(children=[
    html.Img(src=stock_data['Logo'],style={'width':'150px', 'position': 'absolute'}),
    ]),
    html.Div(style={'flex':'0 1 auto' ,'position':'absolute','left':'50%','transform':'translateX(-50%)'},children=[
    html.H1(children='AlgoTrader 0.0',style={'align-self':'center'}),
    ]),
    ]),

    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Div(style={'width': '15%',  'margin-left': 'auto', 'margin-right': 'auto'}, children=[
        dcc.Dropdown(
             id='Filter',
             options=[{'label': "Month", 'value': "Month"},
                      {'label': "Year", 'value': "Year"}],
             value='Year',
             )]),
    html.Div(id='graph_div', className='row', children=[]),



])

app.config['suppress_callback_exceptions'] = True

@app.callback(
    Output('click-data', 'children'),
    [Input('graph', 'clickData')])
def display_hover_data(clickData):
    try:
        dates = clickData['points'][0]["x"]
        new_title_data = article_title_data.loc[article_title_data['date'] == str(
            dates).strip()]
        headings = []

        headings.append(html.Tr([
            html.Th("Article Title"),
            html.Th("Sentiment")
        ])
        )
        for i in new_title_data.index[:3]:
            title_senti = html.Td(
                round(new_title_data['sentiment'][i], 2), style={'color': 'green'})
            title_name = html.Td(
                html.A(f"{new_title_data['title'][i]}", href=new_title_data['URL'][i]))
            headings.append(html.Tr(children=[title_name, title_senti]))

        for i in new_title_data.index[len(new_title_data)-3:len(new_title_data)]:
            title_senti = html.Td(round(new_title_data['sentiment'][i], 2))
            title_name = html.Td(
                html.A(f"{new_title_data['title'][i]}", href=new_title_data['URL'][i]))
            headings.append(html.Tr(children=[title_name, title_senti]))
    except:
        headings = traceback.print_exc()

    return headings


@app.callback(
    Output('news_title', 'children'),
    [Input('graph', 'clickData')])
def display_hover_data(clickData):
    title_date = clickData['points'][0]["x"]
    return None


@app.callback(
    Output('graph_div', 'children'),
    [Input('Filter', 'value')])
def full_graph(value):

    if value == "Year":
        graph = html.Div(children=[
            dcc.Graph(
                id='graph',
                figure={
                    'data': [
                        main_price_plot,
                    ],
                    'layout': {
                        'title': graph_title,
                        'clickmode': 'event+select',
                        'paper_bgcolor': 'rgba(0,0,0,0)',
                        'plot_bgcolor': 'rgba(0,0,0,0)',
                    }
                }

            ),
            html.H6(f"{len(mvs)} position(s) closed."),
            html.H6(f"{trades}"),
        ]
        )

    if value == "Month":

        graph = [
            html.Div(className='two-thirds column', children=[
                dcc.Graph(
                    id='graph',
                    figure={
                        'data': [
                            open_price_plot,
                            buy_annotations,
                            sell_annotations,
                        ],
                        'layout': {
                            'title': graph_title,
                            'clickmode': 'event+select',
                            'paper_bgcolor': 'rgba(0,0,0,0)',
                            'plot_bgcolor': 'rgba(0,0,0,0)',
                            'legend': {'orientation': "h"},
                        }
                    }

                ),
                html.H6(f"{len(mvs)} position(s) closed."),
                html.H6(f"{trades}"),
            ]),
            html.Div(className='four columns', children=[
                html.H4(id="news_title", children="Click to see news headlines!"),
                html.Div(style={'margin-left': 'auto', 'margin-right': 'auto'}, children=[
                    html.Table(className="center", id='click-data', children=[
                        html.Tr([
                            html.Th("Article Title"),
                            html.Th("Sentiment")
                        ]),
                    ])
                ])
            ])]

    return graph


if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=5500)
