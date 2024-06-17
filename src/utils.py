# -*- coding: utf-8 -*-

"""

"""
import datetime
from typing import List

import geopy
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
from pvlib import solarposition

__author__ = "Vegard Ulriksen Solberg"
__email__ = "vegardsolberg@hotmail.com"

from src.config import Config
from src.items import LOCATOR, LAT, LON

env = Config()

class SolarPath:
    def __init__(self, location=None, lat=None, lon=None, timezone="Europe/Oslo"):
        self._location = location
        self._lat = lat
        self._lon = lon
        self._update_data = False
        self.c = 0.001
        self._timezone = timezone
        self._solar_position_data = self.create_solarposition_year_data()
        self._sunset_data = self.create_sunrise_sunset_data()

    @property
    def solar_position_data(self):
        if self._update_data:
            self.update_data()

        return self._solar_position_data

    @solar_position_data.setter
    def solar_position_data(self, data):
        self._solar_position_data = data

    @property
    def sunset_data(self):
        if self._update_data:
            self.update_data()

        return self._sunset_data

    @sunset_data.setter
    def sunset_data(self, data):
        self._sunset_data = data

    def update_data(self):
        self.solar_position_data = self.create_solarposition_year_data()
        self.sunset_data = self.create_sunrise_sunset_data()
        self._update_data = False

    @property
    def base_year(self) -> int:
        return datetime.datetime.today().year

    @property
    def timezone(self) -> str:
        return self._timezone

    @property
    def lat(self) -> float:
        if not self._lat:
            return LAT
        return self._lat

    @property
    def lon(self) -> float:
        if not self._lon:
            return LON
        return self._lon

    @property
    def location(self) -> str:
        return self._location

    @timezone.setter
    def timezone(self, timezone: str):
        if timezone != self._timezone:
            self._update_data = True
            self._timezone = timezone

    @lat.setter
    def lat(self, lat: float):
        if lat != self._lat:
            self._update_data = True
            self._lat = lat

    @lon.setter
    def lon(self, lon: float):
        if lon != self._lon:
            self._update_data = True
            self._lon = lon

    @location.setter
    def location(self, location: str):
        if location != self._location:
            self._update_data = True
            self._location = location

    def create_solarposition_year_data(self) -> pd.DataFrame:
        year_range = pd.date_range(
            f"01/01/{self.base_year} 00:00:00",
            f"31/12/{self.base_year} 23:00:00",
            freq="h",
            tz=self.timezone,
        )
        data = solarposition.get_solarposition(year_range, self.lat, self.lon)
        data["date"] = data.index
        lon_factor = 1 / np.cos(np.radians(self.lat))
        azimuth = np.radians(data["azimuth"])
        elevation = np.radians(data["elevation"])
        data["lat"] = self.lat + self.c * np.cos(azimuth) * np.cos(elevation)
        data["lon"] = self.lon + self.c * lon_factor * np.sin(azimuth) * np.cos(
            elevation
        )
        return data

    def create_sunrise_sunset_data(self) -> pd.DataFrame:
        year_range = pd.date_range(
            f"01/01/{self.base_year} 00:00:00",
            f"31/12/{self.base_year} 23:00:00",
            freq="D",
            tz=self.timezone,
        )
        data = solarposition.sun_rise_set_transit_spa(year_range, self.lat, self.lon)
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

    def create_today_data(self, date: str) -> pd.DataFrame:
        data = self.solar_position_data
        sun_hours = data[data["elevation"] > 0]
        today_data = sun_hours.loc[date]
        return today_data

    def get_map_hovertext(self, today_data: pd.DataFrame) -> List[str]:
        hour_texts = []
        for timestamp, row in today_data.iterrows():
            hour_str = f"<b>Hour {row.name.hour}</b><br>"
            hour_str += f"Elevation: {row.apparent_elevation:.2f} °<br>"
            hour_str += f"Azimuth: {row.azimuth:.2f} °<br>"
            hour_str += f"Zenith: {row.zenith:.2f} °<br>"
            hour_texts.append(hour_str)
        return hour_texts

    def create_map(self, date: str, map_style: str = "satellite-streets") -> go.Figure:
        today_data = self.create_today_data(date=date)
        hours = [str(hour) for hour in today_data.index.hour]

        fig = go.Figure(
            go.Scattermapbox(
                lat=today_data["lat"],
                lon=today_data["lon"],
                mode="markers+text",
                hoverinfo="text",
                marker=go.scattermapbox.Marker(size=22, color="orange"),
                hovertext=self.get_map_hovertext(today_data),
                text=hours,
                name="Hour of the day",
                textfont=dict(size=15, color="black"),
            )
        )

        fig.add_trace(
            go.Scattermapbox(
                lat=[self.lat],
                lon=[self.lon],
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
                accesstoken=env.token,
                bearing=0,
                center=go.layout.mapbox.Center(lat=self.lat, lon=self.lon),
                pitch=0,
                zoom=16,
            ),
            margin=dict(l=10, r=10, b=10, t=70),
            legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor=None),
            title=self.get_title_components(f"Solar position for each hour on {date}"),
        )

        return fig

    def sunrise_figure(self) -> go.Figure:
        base_year = datetime.datetime.today().year
        data = self.sunset_data
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
            title=self.get_title_components(
                f"Sunrise, sunset and transit for {base_year}"
            ),
        )
        return fig

    def analemma_figure(self) -> go.Figure:
        base_year = datetime.datetime.today().year
        data = self.solar_position_data
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
            title=self.get_title_components(
                f"Analemma for each hour of the day for {base_year}"
            ),
            margin=dict(t=70),
        )
        return fig

    def get_title_components(self, title: str) -> dict:
        return dict(
            yanchor="top", y=0.96, xanchor="center", x=0.5, text=f"<b>{title}</b>"
        )

    def update_attributes(self, lat: float, lon: float, location: str, timezone: str):
        if lat is not None and lon is not None:
            pass

        elif location is not None and (lat is None and lon is None):
            lat, lon = self.get_coordinates(location)

        else:
            lat, lon = LAT, LON
        self.lat, self.lon, self.location, self.timezone = lat, lon, location, timezone

    def get_coordinates(self, location: str) -> List[float]:
        geo_location: geopy.location.Location = LOCATOR.geocode(location)
        if geo_location is None:
            raise ValueError("Geo location not found")
        return [geo_location.latitude, geo_location.longitude]
