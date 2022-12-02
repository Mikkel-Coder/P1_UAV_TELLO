import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output


# data = pd.read_csv('data.csv')
# fig  = px.density_mapbox(data, lat='latitude', lon='longitude', z='count', hover_name='count', mapbox_style="open-street-map",)
data = pd.read_csv('data.csv')
fig = px.density_mapbox(data, lat='latitude', lon='longitude',
                        z='count', hover_name='count', mapbox_style="open-street-map",)

app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        dcc.Graph(figure=fig, animate=True),
        dcc.Interval(id='interval'),
    ]),
    html.Div( className='button', children=[
        html.A(html.Button('Refresh Pages'), href='/', className='mr-1'),
    ]),
    html.Div(id='test', children=[
        html.P()
    ])

])


@app.callback(
    Output('test', 'children'),
    Input('interval', 'n_intervals')

)
def update(n):
    new_data = pd.read_csv('data.csv')
    if data.equals(new_data) == False:
        # reload page
        pass


if __name__ == '__main__':
    app.run_server(port=80, debug=True)
