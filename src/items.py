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
