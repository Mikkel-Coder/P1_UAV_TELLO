import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash


# data = pd.read_csv('data.csv')
# fig  = px.density_mapbox(data, lat='latitude', lon='longitude', z='count', hover_name='count', mapbox_style="open-street-map",)
data = pd.read_csv('data.csv')
fig = px.density_mapbox(data, lat='latitude', lon='longitude',
                        z='count', hover_name='count', mapbox_style="open-street-map",)

app = Dash(__name__, use_pages=True)

app.layout = html.Div([
       html.Div(
        [
            html.Div(
                dcc.Link(
                    f"{page['name']} - {page['path']}", href=page["relative_path"]
                )
            )
            for page in dash.page_registry.values()
        ]
    ),

	dash.page_container
])


if __name__ == '__main__':
    app.run_server(port=80, debug=True)
