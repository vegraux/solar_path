# -*- coding: utf-8 -*-

"""

"""
import datetime
import os
from typing import List

import dotenv
import geopy
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from pvlib import solarposition

__author__ = "Vegard Ulriksen Solberg"
__email__ = "vegardsolberg@hotmail.com"

dotenv.load_dotenv(dotenv.find_dotenv())
from src.items import LOCATOR, LAT, LON


def create_year_data(lat, lon, base_year, timezone):
    year_range = pd.date_range(
        f"01/01/{base_year} 00:00:00",
        f"31/12/{base_year} 23:00:00",
        freq="H",
        tz=timezone,
    )
    data = solarposition.get_solarposition(year_range, lat, lon)
    return data


def create_sunrise_sunset_data(lat, lon, base_year, timezone):
    year_range = pd.date_range(
        f"01/01/{base_year} 00:00:00",
        f"31/12/{base_year} 23:00:00",
        freq="H",
        tz=timezone,
    )
    data = solarposition.sun_rise_set_transit_spa(year_range, lat, lon)
    hour_function = lambda x: pd.to_datetime(
        x.strftime(format="%H:%M:%S"), format="%H:%M:%S"
    )
    data["sunrise_hour"] = data["sunrise"].apply(hour_function)
    data["sunset_hour"] = data["sunset"].apply(hour_function)
    data["transit_hour"] = data["transit"].apply(hour_function)
    data["length_of_day"] = (
        data["sunset_hour"] - data["sunrise_hour"] + pd.to_datetime("1900-01-01")
    )
    return data


def create_today_data(date, lat, lon, timezone, c=0.001):
    data = create_year_data(
        lat=lat, lon=lon, base_year=date.split(".")[0], timezone=timezone
    )
    sun_hours = data[data["elevation"] > 0]
    today_data = sun_hours.loc[date]
    lon_factor = 1 / np.cos(np.radians(lat))
    azimuth = np.radians(today_data["azimuth"])
    elevation = np.radians(today_data["elevation"])
    today_data["lat"] = lat + c * np.cos(azimuth) * np.cos(elevation)
    today_data["lon"] = lon + c * lon_factor * np.sin(azimuth) * np.cos(elevation)
    return today_data


def get_map_hovertext(today_data: pd.DataFrame) -> List[str]:
    hour_texts = []
    for timestamp, row in today_data.iterrows():
        hour_str = f"<b>Hour {row.name.hour}</b><br>"
        hour_str += f"Elevation: {row.apparent_elevation:.2f} °<br>"
        hour_str += f"Azimuth: {row.azimuth:.2f} °<br>"
        hour_str += f"Zenith: {row.zenith:.2f} °<br>"
        hour_texts.append(hour_str)
    return hour_texts


def create_map(
    date: str,
    lat: float = 59.946247,
    lon: float = 10.761360,
    map_style: str = "satellite-streets",
    timezone="Europe/Oslo",
) -> go.Figure:
    today_data = create_today_data(date=date, lat=lat, lon=lon, timezone=timezone)
    hours = [str(hour) for hour in today_data.index.hour]
    mapbox_access_token = os.environ["token"]

    fig = go.Figure(
        go.Scattermapbox(
            lat=today_data["lat"],
            lon=today_data["lon"],
            mode="markers+text",
            hoverinfo="text",
            marker=go.scattermapbox.Marker(size=22, color="orange"),
            hovertext=get_map_hovertext(today_data),
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
        margin=dict(l=10, r=10, b=10, t=70),
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor=None),
        title=get_title_components(f"Solar position for each hour on {date}"),
    )

    return fig


def analemma_figure(lat: float, lon: float, timezone: str = "Europe/Oslo") -> go.Figure:
    base_year = datetime.datetime.today().year
    data = create_year_data(lat, lon, base_year, timezone=timezone)
    data["date"] = data.index
    data["Hour"] = data.index.hour.astype(str)
    fig = px.scatter(
        data,
        x="azimuth",
        y="elevation",
        color="Hour",
        hover_data=["date"],
        labels={"elevation": "Elevation", "azimuth": "Azimuth"},
    )
    fig.update_layout(
        yaxis_ticksuffix="°",
        xaxis_ticksuffix="°",
        title=get_title_components(
            f"Analemma for each hour of the day for {base_year}"
        ),
        margin=dict(t=70),
    )
    return fig


def sunrise_figure(lat: float, lon: float, timezone: str = "Europe/Oslo") -> go.Figure:
    base_year = datetime.datetime.today().year
    data = create_sunrise_sunset_data(lat, lon, base_year, timezone)
    fig = go.Figure()
    sunrise_trace = go.Scatter(
        x=data.index, y=data["sunrise_hour"], name="Sunrise", showlegend=True
    )
    sunset_trace = go.Scatter(
        x=data.index, y=data["sunset_hour"], name="Sunset", showlegend=True
    )
    transit_trace = go.Scatter(
        x=data.index, y=data["transit_hour"], name="Transit", showlegend=True
    )
    fig.add_traces([sunrise_trace, sunset_trace, transit_trace])
    fig.update_layout(
        yaxis={"type": "date", "tickformat": "%X"},
        height=800,
        title=get_title_components(f"Sunrise, sunset and transit for {base_year}"),
    )
    return fig


def get_coordinates(location: str) -> List[float]:
    geo_location: geopy.location.Location = LOCATOR.geocode(location)
    if geo_location is None:
        raise ValueError("Geo location not found")
    return [geo_location.latitude, geo_location.longitude]


def get_title_components(title):
    return dict(yanchor="top", y=0.96, xanchor="center", x=0.5, text=f"<b>{title}</b>")


def determine_lat_lon(lat, lon, location):
    if lat is not None and lon is not None:
        pass

    elif location is not None and (lat is None and lon is None):
        lat, lon = get_coordinates(location)

    else:
        lat, lon = LAT, LON
    return lat, lon
