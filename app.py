# -*- coding: utf-8 -*-

"""

"""
__author__ = "Vegard Ulriksen Solberg"
__email__ = "vegardsolberg@hotmail.com"

import datetime

import dash
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
from src.utils import (
    create_map,
    get_coordinates,
    analemma_figure,
    sunrise_figure,
    determine_lat_lon,
)
from src.items import (
    card_month_slider,
    create_dropdown_mapstyles,
    create_dropdown_timezones,
    LAT,
    LON,
)
import dash_html_components as html
import dash_core_components as dcc

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
    lat, lon = determine_lat_lon(lat, lon, location)
    date = f"{YEAR}.{month:0>2}.{day:0>2}"
    return create_map(
        lat=lat, lon=lon, date=date, map_style=map_style, timezone=timezone
    )


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
    lat, lon = determine_lat_lon(lat, lon, location)
    return analemma_figure(lat=lat, lon=lon, timezone=timezone)


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
    lat, lon = determine_lat_lon(lat, lon, location)
    return sunrise_figure(lat=lat, lon=lon, timezone=timezone)


if __name__ == "__main__":
    app.run_server(port=8051, debug=True)
