# -*- coding: utf-8 -*-

"""

"""
from dash.dependencies import Output, Input, State

__author__ = "Vegard Ulriksen Solberg"
__email__ = "vegardsolberg@hotmail.com"

import dash
import dash_bootstrap_components as dbc
from src.utils import create_map, get_coordinates
from src.items import card_month_slider
import dash_html_components as html
import dash_core_components as dcc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# LAT, LON = 63.420862, 10.502749 # Trondheim
LAT, LON = 59.946247, 10.761360  # Oslo

layout = html.Div(
    [
        html.H1(id="header", children="Solar path"),
        html.P(id="info-text", children="Explore the suns path for a location"),
        dbc.Card(card_month_slider, color="light", inverse=False),
        dbc.Input(id="location-input", type="text", placeholder="Type address or city"),
        html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
        dcc.Graph(id="map-fig", figure=create_map(lat=LAT, lon=LON)),
    ]
)

dcc.Input(id='input-2-state', type='text', value='Canada'),

app.layout = dbc.Container(layout)


@app.callback(Output("map-fig", "figure"),
              [Input("month-slider", "value"), Input('submit-button-state', 'n_clicks')],
              [State("location-input", "value")])
def update_data(month, button, location):
    lat, lon = get_coordinates(location)
    return create_map(lat=lat, lon=lon, date=f"2020.{month}.01")




if __name__ == "__main__":
    app.run_server(port=8051, debug=True)
