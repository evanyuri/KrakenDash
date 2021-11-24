# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from posixpath import join
import dash
from dash.development.base_component import _check_if_has_indexable_children
from dash.html.Col import Col
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import requests
import dash_daq as daq
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import numpy
from datetime import datetime


external_stylesheet = ['style.css']


krakendash = dash.Dash(__name__, external_stylesheets=external_stylesheet)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

krakendash.layout = html.Div(
    
    style={'backgroundColor': colors['background'],'border-radius': '20px'},
    children=[

    
    html.H1(
        style={
            'textAlign': 'center',
        },
        children='Crypto Relative Gains Analysis'),
    dcc.Dropdown(
        style={"margin-left": "30px","margin-right": "100px","margin-bottom": "20px", 'backgroundColor': "#111111"},
        id='demo-dropdown',
        multi= True,
        options=[
            {'label': 'BTC', 'value': 'XBT'},
            {'label': 'XMR', 'value': 'XMR'},
            {'label': 'ETH', 'value': 'ETH'},
            {'label': 'DOGE', 'value': 'DOGE'},
            {'label': 'SUSHI', 'value': 'SUSHI'},
            {'label': 'ADA', 'value': 'ADA'},
            {'label': 'SOL', 'value': 'SOL'},
            {'label': 'XRP', 'value': 'XRP'},
            {'label': 'DOT', 'value': 'DOT'},


     
        ],
        value='XBT',
    ),


html.Div(
    [
    html.H2(
        style={
        'textAlign': 'center',
    },
        children='''
        Days Back From Today
    '''),

    dcc.Input(id="time-window", value = 365, type="number",  min=1, max=1000, debounce=True, style={ 'width':'20%'}),
    ],
    style={'justify-content': 'center', 'align-items': 'center', 'textAlign': 'center',},
    className="mb-3",
),




    html.Div(
        style={
        'textAlign': 'center', 'padding' : '20px'
    },
        children='''
        Absolute Gains
    '''),

    dcc.Graph(
        id='example-graph1',
    ),
    html.Div(
        style={
        'textAlign': 'center',
    },
        children='''
        Relative Gains
    '''),

    html.Div(
        style={'display': 'flex', 'justify-content': 'center', 'column-gap': 20, 'width':300},
        children=[
    daq.ToggleSwitch(
    id='toggle-switch',
    value=True,
    # label='Log Scaled',
    # labelPosition='right',
    ),
        html.H2(
        style={
        'textAlign': 'center',
    },
        children='''
        Logrithmic
    '''),
    ]
    ),


    dcc.Graph(
        id='example-graph2',
    ),    
    html.H2(
        style={
        'textAlign': 'center',
    },
        children='''
        By: Evan Kruchowy
    '''),
])

@krakendash.callback(
    Output('example-graph1', 'figure'),
    Output('example-graph2', 'figure'),
    Input('demo-dropdown', 'value'),
    Input('toggle-switch', 'value'),
    Input('time-window', 'value'),

)
def update_figure(value, toggle, days):
    json_name_map_list = [
        ['XBT','XXBTZUSD'],
        ['XMR','XXMRZUSD'],
        ['ETH','XETHZUSD'],
        ['DOGE','XDGUSD'],
        ['SUSHI','SUSHIUSD'],
        ['ADA','ADAUSD'],
        ['SOL','SOLUSD'],
        ['XRP','XXRPZUSD'],
        ['DOT','DOTUSD'],
        ]

    if days == None:
        days = 365

    json_name_map = pd.DataFrame(json_name_map_list, columns = ['key','jsonName'])
    print(json_name_map)
    window = days*86400
    print('print value: ',value)
    if not isinstance(value, list): value = [value]
    print('print value after made list: ',value)
    fig1 = go.Figure()
    fig2 = go.Figure()
    fig2.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)
    fig1.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)
    for i in value:
        print('print index: ',i)
        query_name = i
        json_name = json_name_map.loc[json_name_map['key'] == i, 'jsonName'].iloc[0]
        print(json_name)
        Selected_coin_query = requests.get('https://api.kraken.com/0/public/OHLC?pair={}USD&interval=1440'.format(query_name))
        dictr_coin = Selected_coin_query.json()
        Coin_Daily_Table = pd.json_normalize(data=dictr_coin, record_path=[['result','{}'.format(json_name)]]).astype(float)
        Coin_Daily_Table = Coin_Daily_Table[Coin_Daily_Table[0] > Coin_Daily_Table[0].max() - window]
        Coin_Daily_Table[0] = pd.to_datetime(Coin_Daily_Table[0],unit='s')
        fig1.add_trace(go.Scatter(x=Coin_Daily_Table[0], y=Coin_Daily_Table[1],
                        mode='lines',
                        showlegend=True,
                        name=i))
        fig1.update_layout(transition_duration=500)
        #Figure 2

        maxValue = Coin_Daily_Table[1].max()
        Coin_Daily_Table[8] = Coin_Daily_Table[1]/maxValue
        if toggle == True:
            Coin_Daily_Table[8] = numpy.log10(9*Coin_Daily_Table[8] +1)
        fig2.update_layout(
        transition_duration=500,
        legend = dict(bgcolor = 'black'))
        fig2.add_trace(go.Scatter(x=Coin_Daily_Table[0], y=Coin_Daily_Table[8],
                    mode='lines',
                    showlegend=True,
                    name=i,))


    return fig1, fig2,

if __name__ == '__main__':
    krakendash.run_server(debug=True)
