import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash


dash.register_page(__name__, path='/graph')

# data = pd.read_csv('data.csv')
# fig  = px.density_mapbox(data, lat='latitude', lon='longitude', z='count', hover_name='count', mapbox_style="open-street-map",)
data = pd.read_csv('data.csv')
fig = px.density_mapbox(data, lat='latitude', lon='longitude',
                        z='count', hover_name='count', mapbox_style="open-street-map",)

layout = html.Div([
    html.Div([
        dcc.Graph(figure=fig, animate=True),
        dcc.Interval(id='interval'),
    ]),
    html.Div( className='button', children=[
        html.A(html.Button('Refresh Pages'), href='/graph', className='mr-1'),
    ]),
    html.Div(id='test', children=[
        html.P()
    ])

])


@dash.callback(
    Output('test', 'children'),
    Input('interval', 'n_intervals')

)
def update(n):
    new_data = pd.read_csv('data.csv')
    if data.equals(new_data) == False:
        return 'New data has been found. Please reload'



