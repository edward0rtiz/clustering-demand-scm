import dash
import os
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from app import app


KIWI_LOGO = "../static/logo.png"

# hypelinks
kiwibot = "https://www.kiwibot.com/"


SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#000000",  # f8f9fa
}


# Function for calling navigation bar
def navigation_bar():
    sidebar = html.Div(
        [
            html.Img(src=KIWI_LOGO, height="40px"),
            html.Hr(),
            html.Hr(),
            html.P(
                "Analytical dashboard for strategic decisions",
            ), html.Hr(),
            dbc.Nav(
                [
                    dbc.NavLink("Descriptive Analytics",
                                href="/analytics", active="exact"),
                    dbc.NavLink("Clustering Analytics",
                                href="/clustering", active="exact"),
                    dbc.NavLink("About Us", href="/about", active="exact"),
                ],
                vertical=True,
                pills=True,
            ),
            html.Div()
        ],
        style=SIDEBAR_STYLE,
    )
    return sidebar
