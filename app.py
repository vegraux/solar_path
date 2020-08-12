# -*- coding: utf-8 -*-

"""

"""
__author__ = "Vegard Ulriksen Solberg"
__email__ = "vegardsolberg@hotmail.com"

import dash
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
from src.utils import create_map, get_coordinates
from src.items import card_month_slider, create_dbc_dropdown, create_dropdown
import dash_html_components as html
import dash_core_components as dcc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])

# LAT, LON = 63.420862, 10.502749 # Trondheim
# LAT, LON = 59.946247, 10.761360  # Oslo
LAT, LON = 62.688885, 9.88625  # Hytta Oppdal
layout = html.Div(
    [
        dbc.Row(dbc.Col(html.H1(id="header", children="Solar path"))),
        dbc.Row(
            dbc.Col(
                html.P(id="info-text", children="Explore the suns path for a location")
            )
        ),
        dbc.Row(dbc.Col(dbc.Card(card_month_slider, color="light", inverse=False))),
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
        dbc.Row(
            [
                dbc.Col(
                    dbc.Input(id="lat-input", type="number", placeholder="Latitude")
                ),
                dbc.Col(
                    dbc.Input(id="lon-input", type="number", placeholder="Longitude")
                ),
                dbc.Col(create_dropdown()),
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(id="submit-button-state", n_clicks=0, children="Submit")
                )
            ]
        ),
        dbc.Row(dbc.Col(dcc.Graph(id="map-fig", figure=create_map(lat=LAT, lon=LON)))),
        html.Br(),
        html.Br(),
    ]
)

app.layout = dbc.Container(layout)


@app.callback(
    Output("map-fig", "figure"),
    [
        Input("month-slider", "value"),
        Input("submit-button-state", "n_clicks"),
        Input("dropdown-mapstyles", "value"),
    ],
    [
        State("location-input", "value"),
        State("lat-input", "value"),
        State("lon-input", "value"),
    ],
)
def update_data(month, button, map_style, location, lat, lon):
    if lat is not None and lon is not None:
        pass

    elif location is not None and (lat is None and lon is None):
        lat, lon = get_coordinates(location)

    else:
        lat, lon = LAT, LON

    return create_map(lat=lat, lon=lon, date=f"2020.{month}.01", map_style=map_style)


if __name__ == "__main__":
    app.run_server(port=8051, debug=True)
