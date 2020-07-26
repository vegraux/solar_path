import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from geopy.geocoders import Nominatim

LOCATOR: Nominatim = Nominatim(user_agent="myGeocoder")

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

map_styles_token = [
    "satellite",
    "satellite-streets",
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


def create_dropdown():
    return (
        dcc.Dropdown(
            id="dropdown-mapstyles",
            options=[{"label": style, "value": style} for style in all_map_styles],
            placeholder="Select map style",
        ),
    )
