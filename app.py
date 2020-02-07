# -*- coding: utf-8 -*-

"""

"""
from dash.dependencies import Output, Input

__author__ = "Vegard Ulriksen Solberg"
__email__ = "vegardsolberg@hotmail.com"

import dash
import dash_bootstrap_components as dbc
from src.utils import create_map, card_month_slider
import dash_html_components as html
import dash_core_components as dcc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

LAT, LON = 63.420862, 10.502749


layout = html.Div(
    [
        html.H1(id="header", children="Solar path"),
        html.P(id="info-text", children="Explore the suns path for a location"),
        dbc.Card(card_month_slider, color="light", inverse=False),
        dcc.Graph(id="map-fig", figure=create_map(lat=LAT, lon=LON)),
    ]
)

app.layout = dbc.Container(layout)


@app.callback(Output("map-fig", "figure"), [Input("month-slider", "value")])
def update_data(month):
    return create_map(lat=LAT, lon=LON, date=f"2020.{month}.01")


if __name__ == "__main__":
    app.run_server(port=8051, debug=True)
