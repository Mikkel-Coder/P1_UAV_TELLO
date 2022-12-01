import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State


app = Dash(__name__)

app.layout = html.Div([
    # html.Button('Submit', id='submit-val'), 
    dcc.Graph(id="live-graph", animate=True),
    dcc.Interval(id = 'graph-update'),
])

@app.callback(
    Output('live-graph', 'figure'),
    Input('graph-update', 'n_intervals'),
)


def update_graph_scatter(n):
    data = None
    fig = None
    data = pd.read_csv('data.csv')
    fig  = px.density_mapbox(data, 
                             lat='latitude', 
                             lon='longitude', 
                             z='count',
                             mapbox_style="open-street-map",)
    print(n)

    return fig 


if __name__ == '__main__':
    app.run_server(debug=True)