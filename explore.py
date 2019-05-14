import pickle
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from datetime import date as dt

import numpy as np
from numpy import array
from datetime import timedelta
import json
import traceback

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import sqlite3

conn = sqlite3.connect('Data/AlgoTrader.db')
article_query = "SELECT * FROM ArticleTitles ORDER BY sentiment DESC;"
main_query = "SELECT * FROM Main;"

article_title_data = pd.read_sql_query(article_query, conn)
main_price_data = pd.read_sql_query(main_query, conn)

conn.commit()
conn.close()


def fix_dates(dates):
    d =datetime.strptime(dates, "%Y-%m-%d %H:%M:%S")
    d = d.strftime("%Y-%m-%d")
    return d


article_title_data['date'] = article_title_data['date'].apply(fix_dates)
main_price_data['date'] = main_price_data['date'].apply(fix_dates)
main_price_data = main_price_data.drop(len(main_price_data)-1)
data = pd.read_csv('SentimentData.csv')

sell_x = []
sell_y = []
buy_x = []
buy_y = []
mvs = []

with open("Data/company_name.txt") as f:
    graph_title = f.read()


# Appends buy/sell/hold into separate lists. (PLEASE MAKE THIS BETTER)
def plot_pos(leverage):

    x_pos = []
    y_pos = []

    bought = False
    sold = False

    pos_value = 0
    movement = 0

    for index, row in data.iterrows():

        position = row['positions']
        price = row['open']

        if position != "hold":
            plt.annotate(position, xy=(row['date'], row['open']))

            if position == "sell":
                sell_x.append(row['date'])
                sell_y.append(row['open'])

                if sold == True:
                    #pos_value = (pos_value - price)/2
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
                buy_y.append(row['open'])

                if bought == True:
                    #pos_value = (pos_value + price)/2
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


senti = data['sentiment']
open_delta = data['open_delta']

open_price = data['open'].drop(len(data)-1)
close_price = data['close']

date = data['date']
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

for i in mvs:
    trades += str(round(i, 2)) + "% |\t"


def create_plot(y_data, x_data=dates):
    standard_plot = go.Scatter(
        x=x_data,
        y=y_data,

        mode='lines',
        name='Open',
    )

    return standard_plot

main_price_plot = create_plot(main_price_data['open'],full_dates)
open_price_plot = create_plot(open_price)
close_price_plot = create_plot(close_price)
open_delta_plot = create_plot(open_delta)

buy_annotations = go.Scatter(
    x=buy_x,
    y=buy_y,
    mode='markers+text',
    name='Buy',
    text="buy",
    hoverinfo='none',
    textposition='middle right'
)

sell_annotations = go.Scatter(
    x=sell_x,
    y=sell_y,
    mode='markers+text',
    name='Sell',
    text="sell",
    hoverinfo='none',
    textposition='middle right'
)

app = dash.Dash(__name__, static_folder='assets')

app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

app.layout = html.Div(children=[
    html.H1(children='AlgoTrader 0.0'),
     
     html.Div(style = {'width': '15%',  'margin-left': 'auto','margin-right': 'auto'},children = [
            dcc.Dropdown(
                id='Filter',
                options=[{'label': "Month", 'value': "Month"},{'label': "Year", 'value': "Year"}] ,
                value='Year',
     )]),
    html.Div(id = 'graph_div',className = 'row',children=[]),

    
])

app.config['suppress_callback_exceptions']=True

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
             title_senti = html.Td(round(new_title_data['sentiment'][i],2), style = {'color':'green'})
             title_name = html.Td(html.A(f"{new_title_data['title'][i]}",href = new_title_data['URL'][i]))
             headings.append(html.Tr(children = [title_name,title_senti]))
        
        for i in new_title_data.index[len(new_title_data)-3:len(new_title_data)]: 
             title_senti = html.Td(round(new_title_data['sentiment'][i],2))
             title_name = html.Td(html.A(f"{new_title_data['title'][i]}",href = new_title_data['URL'][i]))
             headings.append(html.Tr(children = [title_name,title_senti]))
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
        graph = html.Div( children = [
            dcc.Graph(
                id='graph',
                figure={
                    'data': [
                        main_price_plot,
                        #open_price_plot,
                        # close_price_plot,
                        # open_delta_plot,
                        #buy_annotations,
                        #sell_annotations,
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
                html.Div(className = 'two-thirds column',children = [
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
                            'legend':{'orientation':"h"},
                        }
                    }
                
                ),
                html.H6(f"{len(mvs)} position(s) closed."),
                html.H6(f"{trades}"),
            ]),
            html.Div(className = 'four columns',children = [
                html.H4(id = "news_title",children="Click to see news headlines!"),
                html.Div(style = {'margin-left': 'auto','margin-right': 'auto'},children = [
                    html.Table(className = "center",id = 'click-data', children=[
                            html.Tr([
                                html.Th("Article Title"),
                                html.Th("Sentiment")
                                ]),
                            ])
                    ])
                ])]


    return graph

    

if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port=5500)

