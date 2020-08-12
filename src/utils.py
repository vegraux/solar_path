# -*- coding: utf-8 -*-

"""

"""
from typing import List

import geopy
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from pvlib import solarposition

__author__ = "Vegard Ulriksen Solberg"
__email__ = "vegardsolberg@hotmail.com"

from src.items import LOCATOR


def create_year_data(lat, lon, base_year=2020):
    year_range = pd.date_range(
        f"01/01/{base_year} 00:00:00",
        f"31/12/{base_year} 00:00:00",
        freq="H",
        tz="Europe/Oslo",
    )
    data = solarposition.get_solarposition(year_range, lat, lon)
    return data


def create_today_data(date="2020.02.05", lat=59.946247, lon=10.761360, c=0.001):
    data = create_year_data(lat=lat, lon=lon, base_year=date.split(".")[0])
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


def get_hovertext(today_data: pd.DataFrame) -> List[str]:
    hour_texts = []
    for timestamp, row in today_data.iterrows():
        hour_str = f"<b>Hour {row.name.hour}</b><br>"
        hour_str += f"Elevation: {row.apparent_elevation:.2f} °<br>"
        hour_str += f"Azimuth: {row.azimuth:.2f} °<br>"
        hour_str += f"Zenith: {row.zenith:.2f} °<br>"
        hour_texts.append(hour_str)
    return hour_texts


def create_map(date="2020.02.05", lat=59.946247, lon=10.761360, map_style="satellite"):
    today_data = create_today_data(date=date, lat=lat, lon=lon)
    hours = [str(hour) for hour in today_data.index.hour]
    mapbox_access_token = open("src\\mapbox_token.txt").read()

    fig = go.Figure(
        go.Scattermapbox(
            lat=today_data["lat"],
            lon=today_data["lon"],
            mode="markers+text",
            hoverinfo="text",
            marker=go.scattermapbox.Marker(size=22, color="orange"),
            hovertext=get_hovertext(today_data),
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
            style=map_style,
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(lat=lat, lon=lon),
            pitch=0,
            zoom=16,
        ),
        margin=dict(l=10, r=10, b=10, t=10),
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor=None),
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


def get_coordinates(location: str) -> List[float]:
    geo_location: geopy.location.Location = LOCATOR.geocode(location)
    if geo_location is None:
        raise ValueError("Geo location not found")
    return [geo_location.latitude, geo_location.longitude]
