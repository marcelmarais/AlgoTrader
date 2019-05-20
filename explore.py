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
from plotly import tools
from dash.dependencies import Input, Output
from numpy import array

try:
    with open("Data/stock_data.json") as f:
        stock_data = json.load(f)
except:
    print("""
            It looks like you are trying to run the program
            without generating data first.
        """)
    exit()

# All SQL queries happen here:

conn = sqlite3.connect('Data/AlgoTrader.db')

article_query = "SELECT strftime('%Y-%m-%d', date) AS date,sentiment,URL,title FROM ArticleTitles ORDER BY sentiment DESC;"
sentiment_query = "SELECT strftime('%Y-%m-%d', date) AS date,open,close,sentiment,position  FROM Sentiment;"
main_query = "SELECT strftime('%Y-%m-%d', date) AS date,open,volume  FROM Main;"

ma_query = "SELECT strftime('%Y-%m-%d', date) AS date,open,SMA,EMA,MACD,MACDsignal,BollingerLower,BollingerUpper FROM MovingAverages"
momentum_query = "SELECT strftime('%Y-%m-%d', date) AS date,RSI_14,Stoch_RSI_14,OBV,TSI_25_13 FROM Momentum"

article_title_data = pd.read_sql_query(article_query, conn)
main_price_data = pd.read_sql_query(main_query, conn)
sentiment_data = pd.read_sql_query(sentiment_query,conn)

ma_data = pd.read_sql_query(ma_query,conn)
momentum_data = pd.read_sql_query(momentum_query,conn)

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


# All plots are created here:

def create_plot(y_data, x_data=full_dates,name='Open'):
    standard_plot = go.Scatter(
        x=x_data,
        y=y_data,

        mode='lines',
        name=name,
    )

    return standard_plot

# Moving Average Plots

main_price_plot = create_plot(main_price_data['open'])
open_price_plot = create_plot(open_price, dates)
close_price_plot = create_plot(close_price,dates)

sma_plot = create_plot(ma_data['SMA'],name='SMA')
ema_plot = create_plot(ma_data['EMA'],name='EMA')

MACD_plot = create_plot(ma_data['MACD'],name='MACD')
MACD_signal_plot = create_plot(ma_data['MACDsignal'],name='MACD signal')

MACD_with_price = tools.make_subplots(rows=2, cols=1,shared_xaxes=True)

MACD_with_price.append_trace(main_price_plot, 1, 1)
MACD_with_price.append_trace(MACD_plot, 2, 1)
MACD_with_price.append_trace(MACD_signal_plot, 2, 1)

bollinger_lower = create_plot(ma_data['BollingerLower'])
bollinger_upper = create_plot(ma_data['BollingerUpper'])

# Momentum Plots

RSI = create_plot(momentum_data['RSI_14'])

RSI_with_price_plot = tools.make_subplots(rows=2, cols=1,shared_xaxes=True)
RSI_with_price_plot.append_trace(main_price_plot, 1, 1)
RSI_with_price_plot.append_trace(RSI, 2, 1)

TSI = create_plot(momentum_data['TSI_25_13'])
TSI_with_price_plot = tools.make_subplots(rows=2, cols=1,shared_xaxes=True)
TSI_with_price_plot.append_trace(main_price_plot, 1,1)
TSI_with_price_plot.append_trace(TSI, 2,1)

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

# Layouts:

standard_layout = {
    'title': graph_title,
    'clickmode': 'event+select',
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'legend': {'orientation': "h"},
}

# Reusable parts:

profit_loss = html.Div(children = [
    html.H6(f"{len(mvs)} position(s) closed."),
    html.H6(f"{trades}")
])


app = dash.Dash(__name__, static_folder='assets')

app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

app.layout = html.Div(children=[

    html.Div(style={'display':'flex','flex-direction':'row','flex-wrap':'nowrap','position':'relative','justify-content':'flex-start'},
    
    children =[
    
        html.Div(
        children=[
            html.Img(src=stock_data['Logo'],style={'width':'100px', 'position': 'absolute'}),
        ]),
    
        html.Div(
        style={'flex':'0 1 auto' ,'position':'absolute','left':'50%','transform':'translateX(-50%)'},
        children=[
            html.H1(children='AlgoTrader 0.0',style={'align-self':'center'}),
        ]),
    ]),
    
    html.Div(style = {'height':'110px'}),

    html.Div(style={'width': '25%',  'margin-left': 'auto', 'margin-right': 'auto'}, children=[
        dcc.Dropdown(
             id='Filter',
             options=[{'label': "Sentiment", 'value': "sentiment"},
                      {'label': "Moving Averages", 'value': "moving_average"},
                      {'label': "Momentum Indicators", 'value': "momentum"}],
             value='moving_average',
        )
    ]),
    
    html.Div(id='graph_div', className='row', children=[]),

])

app.config['suppress_callback_exceptions'] = True

@app.callback(#Fix this / make a decision
    Output('news_title', 'children'),
    [Input('graph', 'clickData')])
def display_hover_data(clickData):
    try:
        title_date = clickData['points'][0]["x"]
    except:
        pass
    return None

@app.callback(
    Output('click-data', 'children'),
    [Input('graph', 'clickData')])
def display_click_data(clickData):
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
    Output('graph_div', 'children'),
    [Input('Filter', 'value')])
def full_graph(value):

    if value == "moving_average":
        graph = html.Div(children=[

            dcc.RadioItems(
                id='radio-items',
                options = [
                    {'label': 'SMA', 'value': 'sma'},
                    {'label': 'EMA', 'value': 'ema'},
                    {'label': 'MACD', 'value': 'macd'},
                    {'label': 'Bollinger', 'value': 'bollinger'},
                ],
                value = "sma",
                labelStyle={'display': 'inline-block'}
            ),
            dcc.Graph(
                id='moving_average',
                figure={
                    'data': [
                        main_price_plot,
                    ],

                    'layout': standard_layout
                }
            ),

            profit_loss,
        ]
        )
    if value == "momentum":
        graph = html.Div(children=[

            dcc.RadioItems(
                id='momentum-items',
                options = [
                    {'label': 'RSI', 'value': 'rsi'},
                    {'label': 'TSI', 'value': 'tsi'},
                ],
                value = "rsi",
                labelStyle={'display': 'inline-block'}
            ),
            dcc.Graph(
                id='momentum',
                figure={
                    'data': [
                        main_price_plot,
                    ],

                    'layout': standard_layout
                }
            ),

            profit_loss,
        ]
        )

    if value == "sentiment":

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
                        'layout': standard_layout
                    }
                ),

                profit_loss,
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

@app.callback(Output('moving_average', 'figure'),
    [Input('radio-items', 'value')])
def moving_averages(value):
    data = {}

    if value == 'sma':

        data = {
                    'data': [
                        main_price_plot,
                        sma_plot,
                    ],
                    'layout': standard_layout
                }

    if value == 'ema':

        data = {
                    'data': [
                        main_price_plot,
                        ema_plot,
                    ],
                    'layout': standard_layout
                }
    
    if value == 'macd':
        data = MACD_with_price

    if value == 'bollinger':
        data = {
                    'data': [
                        main_price_plot,
                        bollinger_lower,
                        bollinger_upper,
                    ],
                    'layout': standard_layout
                }
    return data

@app.callback(Output('momentum', 'figure'),
    [Input('momentum-items', 'value')])
def moving_averages(value):
    data = {}

    if value == 'rsi':
        data = RSI_with_price_plot
    
    if value == 'tsi':
        data = TSI_with_price_plot

    return data


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=5500)
