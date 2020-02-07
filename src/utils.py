# -*- coding: utf-8 -*-

"""

"""

import numpy as np
import plotly.graph_objects as go
import pandas as pd
from pvlib import solarposition

import dash_bootstrap_components as dbc
import dash_core_components as dcc

import dash_html_components as html

__author__ = "Vegard Ulriksen Solberg"
__email__ = "vegardsolberg@hotmail.com"


def create_year_data(base_year=2020):
    year_range = pd.date_range(
        f"01/01/{base_year} 00:00:00",
        f"31/12/{base_year} 00:00:00",
        freq="H",
        tz="Europe/Oslo",
    )
    lat, lon = 59.946247, 10.761360
    data = solarposition.get_solarposition(year_range, lat, lon)
    return data


def create_today_data(date="2020.02.05", lat=59.946247, lon=10.761360, c=0.001):
    data = create_year_data(date.split(".")[0])
    sun_hours = data[data["elevation"] > 0]
    today_data = sun_hours.loc[date]
    lon_factor = 1 / np.cos(np.radians(lat))
    today_data["lat"] = lat + c * np.cos(np.radians(today_data["azimuth"])) * np.cos(
        np.radians(today_data["elevation"])
    )
    today_data["lon"] = lon + c * lon_factor * np.sin(
        np.radians(today_data["azimuth"])
    ) * np.cos(np.radians(today_data["elevation"]))

    return today_data


def create_map(date="2020.02.05", lat=59.946247, lon=10.761360):
    today_data = create_today_data(date=date, lat=lat, lon=lon)
    hours = [str(hour) for hour in today_data.index.hour]
    mapbox_access_token = open("src\\mapbox_token.txt").read()

    fig = go.Figure(
        go.Scattermapbox(
            lat=today_data["lat"],
            lon=today_data["lon"],
            mode="markers+text",
            marker=go.scattermapbox.Marker(size=22, color="orange"),
            text=hours,
            name="Hour of the day",
            textfont=dict(family="sans serif", size=18, color="black"),
        )
    )

    fig.add_trace(
        go.Scattermapbox(
            lat=[lat],
            lon=[lon],
            mode="markers+text",
            name="Position",
            marker=go.scattermapbox.Marker(size=14, color="blue"),
        )
    )

    fig.update_layout(
        autosize=True,
        hovermode="closest",
        height=700,
        mapbox=go.layout.Mapbox(
            style="outdoors",
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(lat=lat, lon=lon),
            pitch=0,
            zoom=16,
        ),
    )

    return fig


def create_scattermap(today_data):
    hours = [str(hour) for hour in today_data.index.hour]

    return go.Scattermapbox(
        lat=today_data["lat"],
        lon=today_data["lon"],
        mode="markers+text",
        marker=go.scattermapbox.Marker(size=22, color="yellow"),
        text=hours,
        name="Hour of the day",
        textfont=dict(family="sans serif", size=18, color="black"),
    )


def create_animated_map(lat=59.946247, lon=10.761360):
    mapbox_access_token = open("mapbox_token.txt").read()

    fig = go.Figure(
        data=go.Scattermapbox(
            lat=[lat],
            lon=[lon],
            mode="markers+text",
            name="Position",
            marker=go.scattermapbox.Marker(size=14, color="blue"),
        ),
        layout=go.Layout(
            autosize=True,
            hovermode="closest",
            height=700,
            mapbox=go.layout.Mapbox(
                accesstoken=mapbox_access_token,
                bearing=0,
                center=go.layout.mapbox.Center(lat=lat, lon=lon),
                pitch=0,
                zoom=16,
            ),
            updatemenus=[
                dict(
                    type="buttons",
                    buttons=[dict(label="Play", method="animate", args=[None])],
                )
            ],
        ),
        frames=[
            go.Frame(
                data=[
                    create_scattermap(create_today_data(date))
                    for date in [
                        "2020.02.05",
                        "2020.03.05",
                        "2020.04.05",
                        "2020.05.05",
                        "2020.06.05",
                    ]
                ]
            )
        ],
    )

    fig.show()


month_map = {
    1: "jan",
    2: "feb",
    3: "mar",
    4: "april",
    5: "may",
    6: "june",
    7: "july",
    8: "aug",
    9: "sep",
    10: "oct",
    11: "nov",
    12: "dec",
}

card_month_slider = [
    dbc.CardBody(
        [
            html.H5("Select month", className="card-title"),
            html.P("Pull the slider to see the month", className="card-text"),
            dcc.Slider(
                id="month-slider",
                min=1,
                max=12,
                step=1,
                value=1,
                marks={k: month_map[k] for k in range(1, 13)},
            ),
        ]
    )
]
