# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import requests
import dash_daq as daq
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import numpy

external_stylesheet = ['style.css']


krakendash = dash.Dash(__name__, external_stylesheets=external_stylesheet)


colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

serverTime = requests.get('https://api.kraken.com/0/public/Time') #Get Server Time
systemStatus = requests.get('https://api.kraken.com/0/public/SystemStatus') #Get System Status
assetInfo = requests.get('https://api.kraken.com/0/public/Time') #Get Asset Info
assetPairs = requests.get('https://api.kraken.com/0/public/AssetPairs?pair=XXBTZUSD,XXETHXXBT') #Get Tradable Asset Pairs
tickerInfo = requests.get('https://api.kraken.com/0/public/Ticker?pair=XBTUSD') #Get Ticker Information
ohlcData_XBT = requests.get('https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=1440') #Get OHLC Data (interval in minutes)
ohlcData_XMR = requests.get('https://api.kraken.com/0/public/OHLC?pair=XMRUSD&interval=1440') #Get OHLC Data (interval in minutes)
ohlcData_XETH = requests.get('https://api.kraken.com/0/public/OHLC?pair=ETHUSD&interval=1440') #Get OHLC Data (interval in minutes)

print(assetPairs.json())
dictr_XBT = ohlcData_XBT.json()
dictr_XMR = ohlcData_XMR.json()
dictr_XETH = ohlcData_XETH.json()


#print(dictr_XETH)
BTCEUR_Daily_Table_XBT = pd.json_normalize(data=dictr_XBT, record_path=[['result','XXBTZUSD']]).astype(float)
BTCEUR_Daily_Table_XMR = pd.json_normalize(data=dictr_XMR, record_path=[['result','XXMRZUSD']]).astype(float)
BTCEUR_Daily_Table_ETH = pd.json_normalize(data=dictr_XETH, record_path=[['result','XETHZUSD']]).astype(float)

fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=BTCEUR_Daily_Table_XBT[0], y=BTCEUR_Daily_Table_XBT[1],
                    mode='lines',
                    name='lines'))
fig1.add_trace(go.Scatter(x=BTCEUR_Daily_Table_XMR[0], y=BTCEUR_Daily_Table_XMR[1],
                    mode='lines',
                    name='lines'))
fig1.add_trace(go.Scatter(x=BTCEUR_Daily_Table_ETH[0], y=BTCEUR_Daily_Table_ETH[1],
                    mode='lines',
                    name='lines'))                    
fig1.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

#relative values 
maxXBT = BTCEUR_Daily_Table_XBT[1].max()
maxXMR = BTCEUR_Daily_Table_XMR[1].max()
maxETH = BTCEUR_Daily_Table_ETH[1].max()

BTCEUR_Daily_Table_XBT[8] = 9*BTCEUR_Daily_Table_XBT[1]/maxXBT +1
BTCEUR_Daily_Table_XMR[8] = 9*BTCEUR_Daily_Table_XMR[1]/maxXMR +1
BTCEUR_Daily_Table_ETH[8] = 9*BTCEUR_Daily_Table_ETH[1]/maxETH +1


fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=BTCEUR_Daily_Table_XBT[0], y=numpy.log10(BTCEUR_Daily_Table_XBT[8]),
                    mode='lines',
                    name='lines'))
fig2.add_trace(go.Scatter(x=BTCEUR_Daily_Table_XMR[0], y=numpy.log10(BTCEUR_Daily_Table_XMR[8]),
                    mode='lines',
                    name='lines'))
fig2.add_trace(go.Scatter(x=BTCEUR_Daily_Table_ETH[0], y=numpy.log10(BTCEUR_Daily_Table_ETH[8]),
                    mode='lines',
                    name='lines'))                    
fig2.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)



# max2 = BTCEUR_Daily_Table_XBT[1].max()
# BTCEUR_Daily_Table_XBT[8] = BTCEUR_Daily_Table_XBT[1]/max2
# fig2 = px.line(BTCEUR_Daily_Table_XBT, x=0,y=8)
# fig2.update_layout(
#     plot_bgcolor=colors['background'],
#     paper_bgcolor=colors['background'],
#     font_color=colors['text']
# )

krakendash.layout = html.Div(
    
    style={'backgroundColor': colors['background']},
    children=[

    
    html.H1(
        style={
            'textAlign': 'center',
            'color': colors['text']
        },
        children='Crypto Relative Gains Analysis'),
    dcc.Dropdown(
        id='demo-dropdown',
        options=[
            {'label': 'BTC', 'value': 'XBT'},
            {'label': 'XMR', 'value': 'XMR'},
     
        ],
        value='XBT'
    ),
    html.Div(id='dd-output-container'),

    html.Div(
        style={
        'textAlign': 'center',
        'color': colors['text']
    },
        children='''
        Absolute Gains
    '''),

    dcc.Graph(
        id='example-graph1',
        figure=fig1
    ),

        html.Div(
        style={
        'textAlign': 'center',
        'color': colors['text']
    },
        children='''
        Relative Gains
    '''),

        dcc.Graph(
        id='example-graph2',
        figure=fig2
    )
])

@krakendash.callback(
    Output('dd-output-container', 'children'),
    Input('demo-dropdown', 'value')
)
def update_output(value):
    return 'You have selected "{}"'.format(value)


if __name__ == '__main__':
    krakendash.run_server(debug=False)
