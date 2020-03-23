import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


df =  pd.DataFrame(pd.read_csv('/Users/damurphy/Desktop/COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/03-21-2020.csv'))
sub_df = df[df['Country/Region']=='US']
# Main, filtered dataset
us_land_df = sub_df[sub_df['Province/State'] != 'US']
# Supporting datasets
confirmed_df = us_land_df['Confirmed']
recovered_df = us_land_df['Recovered']
death_df = us_land_df['Deaths']

app.layout = html.Div([
    html.H1("Confirmed Coronavirus Cases (3/21/2020)"),
    dcc.Graph(
        id = 'indicator-graphic',
        style={'height':'750px', 'width':'100%'},
        figure={
            'data':[
                dict(
                    x = us_land_df['Province/State'],
                    y = us_land_df['Confirmed'],
                    text = us_land_df['Confirmed'],
                    mode= 'markers',
                    opacity=.6,
                    marker={
                        'size': 10,
                        'line': {'width':1, 'color':'blue'}
                    },
                    # name=i,
                )#for i in us_land_df['Province/State']
            ],
            'layout':dict(
                xaxis={'type':'normal', 'title':'State or US Territory'},
                yaxis={'title':'Confirmed Coronavirus Cases'},
                hovermode='closest'  
            )
        }
    ),
    html.Br(),
    html.Div(
        html.P("Toggle between log and normal to transform the y-axis!"),
        style={'width': '49%', 'padding': 'px 20px 20px 20px'}
    ),
    dcc.Dropdown(
        id='yaxis-type',
        options=[{'label': i, 'value': i} for i in ['normal', 'log']],
        value='Coronavirus Cases Confirmed (US)'
    )
]
)

@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('yaxis-type', 'value')])
def update_graph(yaxis_type):
    return {
            'data':[
                dict(
                    x = us_land_df['Province/State'],
                    y = us_land_df['Confirmed'],
                    text = us_land_df['Province/State'],
                    mode= 'markers',
                    opacity=.6,
                    marker={
                        'size': 10,
                        'line': {'width':1, 'color':'blue'}
                    },
                    
                    # name=i,
                )#for i in us_land_df['Province/State']
            ],
            'layout': dict(
                xaxis={'title':'State or US Territory'},
                yaxis={'type': 'linear' if 'yaxis-type' == 'normal' else 'log'},
                hovermode='closest',   
                            
            ),        
        'layout': dict(
        yaxis={
            'title': 'Confirmed Coronavirus Cases',
            'type': 'linear' if yaxis_type=='normal' else 'log',
        },
        hovermode='closest'
    )
 }
if __name__ == '__main__':
    app.run_server(debug=True)