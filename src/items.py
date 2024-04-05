import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
import pytz
from geopy.geocoders import Nominatim

LOCATOR = Nominatim(user_agent="myGeocoder")

# LAT, LON = 63.420862, 10.502749 # Trondheim
# LAT, LON = 59.946247, 10.761360  # Oslo
LAT, LON = 59.940606, 10.758659  # Larviksgata

# LAT, LON = 62.688885, 9.88625  # Hytta Oppdal

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
            html.H5("Select month and day", className="card-title"),
            html.P("Pull the sliders to change month and day", className="card-text"),
            dcc.Slider(
                id="month-slider",
                min=1,
                max=12,
                step=1,
                value=1,
                marks={k: month_map[k] for k in range(1, 13)},
            ),
            dcc.Slider(
                id="day-slider",
                min=1,
                max=31,
                step=1,
                value=1,
                marks={k: str(k) for k in range(1, 32)},
            ),
        ]
    )
]


map_styles_token = [
    "satellite-streets",
    "satellite",
    "basic",
    "streets",
    "outdoors",
    "light",
    "dark",
    "open-street-map",
]
map_styles_free = [
    "carto-positron",
    "carto-darkmatter",
    "stamen-terrain",
    "stamen-toner",
    "stamen-watercolor",
]

all_map_styles = map_styles_token + map_styles_free


def all_timezones():
    timezones = [k for k in pytz.all_timezones]
    timezones.remove("Europe/Oslo")
    timezones.remove("UTC")
    return ["Europe/Oslo", "UTC"] + timezones


def create_dbc_dropdown():
    """Nice looking, but unpractical to use in callbacks"""

    dropdown = [dbc.DropdownMenuItem("No token required", header=True)]
    dropdown.extend([dbc.DropdownMenuItem(map_style) for map_style in map_styles_free])
    dropdown.extend(
        [
            dbc.DropdownMenuItem(divider=True),
            dbc.DropdownMenuItem("Token required", header=True),
        ]
    )
    dropdown.extend([dbc.DropdownMenuItem(map_style) for map_style in map_styles_token])
    return dbc.DropdownMenu(dropdown, label="Map style", id="map-style-dropdown")


def create_dropdown_mapstyles():
    return (
        dcc.Dropdown(
            id="dropdown-mapstyles",
            options=[{"label": style, "value": style} for style in all_map_styles],
            placeholder="Select map style",
            value="satellite-streets",
        ),
    )


def create_dropdown_timezones():
    return (
        dcc.Dropdown(
            id="dropdown-timezones",
            options=[{"label": tz, "value": tz} for tz in all_timezones()],
            placeholder="Select timezone",
            value="Europe/Oslo",
        ),
    )
