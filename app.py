# -*- coding: utf-8 -*-

"""

"""
__author__ = "Vegard Ulriksen Solberg"
__email__ = "vegardsolberg@hotmail.com"

import datetime

import dash
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc

from src.utils import SolarPath
from src.items import (
    card_month_slider,
    create_dropdown_mapstyles,
    create_dropdown_timezones,
)
from dash import html
from dash import dcc

solar = SolarPath()
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])

YEAR = datetime.datetime.today().year
layout = html.Div(
    [
        dbc.Row(dbc.Col(html.H1(id="header", children="Solar path"))),
        dbc.Row(
            dbc.Col(
                html.P(id="info-text", children="Explore the suns path for a location")
            )
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Input(
                        id="location-input",
                        type="text",
                        placeholder="Type address or city",
                    )
                )
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Input(id="lat-input", type="number", placeholder="Latitude")
                ),
                dbc.Col(
                    dbc.Input(id="lon-input", type="number", placeholder="Longitude")
                ),
                dbc.Col(create_dropdown_mapstyles()),
                dbc.Col(create_dropdown_timezones()),
                dbc.Col(
                    dbc.Button(id="submit-button-state", n_clicks=0, children="Submit")
                ),
            ]
        ),
        html.Br(),
        dbc.Row(dbc.Col(dbc.Card(card_month_slider, color="light", inverse=False))),
        dcc.Graph(id="map-fig"),
        dcc.Graph(id="sunrise-fig"),
        dcc.Graph(id="analemma-fig"),
        html.Br(),
        html.Br(),
    ]
)

app.layout = dbc.Container(layout)


@app.callback(
    Output("map-fig", "figure"),
    [
        Input("month-slider", "value"),
        Input("day-slider", "value"),
        Input("submit-button-state", "n_clicks"),
        Input("dropdown-mapstyles", "value"),
        Input("dropdown-timezones", "value"),
    ],
    [
        State("location-input", "value"),
        State("lat-input", "value"),
        State("lon-input", "value"),
    ],
)
def update_map_figure(month, day, button, map_style, timezone, location, lat, lon):
    solar.update_attributes(lat, lon, location, timezone)
    date = f"{YEAR}.{month:0>2}.{day:0>2}"
    return solar.create_map(date=date, map_style=map_style)


@app.callback(
    Output("analemma-fig", "figure"),
    [Input("submit-button-state", "n_clicks"), Input("dropdown-timezones", "value")],
    [
        State("location-input", "value"),
        State("lat-input", "value"),
        State("lon-input", "value"),
    ],
)
def update_analemma_figure(button, timezone, location, lat, lon):
    solar.update_attributes(lat, lon, location, timezone)
    return solar.analemma_figure()


@app.callback(
    Output("sunrise-fig", "figure"),
    [Input("submit-button-state", "n_clicks"), Input("dropdown-timezones", "value")],
    [
        State("location-input", "value"),
        State("lat-input", "value"),
        State("lon-input", "value"),
    ],
)
def update_sunrise_figure(button, timezone, location, lat, lon):
    solar.update_attributes(lat, lon, location, timezone)
    return solar.sunrise_figure()


if __name__ == "__main__":
    app.run_server(port=8051, debug=True)
