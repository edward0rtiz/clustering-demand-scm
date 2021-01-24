import os

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from app import app

from lib import analytics, clustering, home, about

KIWI_LOGO = "../assets/logo.png"

# hypelinks
kiwibot = "https://www.kiwibot.com/"


SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16%",
    "padding": "2rem 1rem",
    "background-color": "#000000",
}


# Function for calling navigation bar
def navigation_bar():
    sidebar = html.Div(
        [
            dbc.Button(
                [html.Img(src=KIWI_LOGO, style={"width": "100%"}, alt="Null")],
                href=kiwibot,
                color="None",
                block=True,
            ),
            html.Hr(),
            # html.H4(
            #    "Analytical dashboard for strategic decisions",
            #    style={"font-size": "1.2rem", "height": "60px", "text-align": "center"},
            # ),
            html.Hr(),
            html.Hr(),
            html.Hr(),
            dbc.Nav(
                [
                    dbc.NavLink(
                        "Home",
                        href="/home",
                        active=True,
                        style={
                            "width": "100%",
                            "font-size": "1rem",
                            "color": "#FFFFFF",
                        },
                    ),
                    dbc.NavLink(
                        "Descriptive Analytics",
                        href="/analytics",
                        active=True,
                        style={
                            "width": "100%",
                            "font-size": "1rem",
                            "color": "#FFFFFF",
                        },
                    ),
                    dbc.NavLink(
                        "Clustering Analytics",
                        href="/clustering",
                        active=True,
                        style={
                            "width": "100%",
                            "font-size": "1rem",
                            "color": "#FFFFFF",
                        },
                    ),
                    dbc.NavLink(
                        "About Us",
                        href="/about",
                        active=True,
                        style={
                            "width": "100%",
                            "font-size": "1rem",
                            "color": "#FFFFFF",
                        },
                    ),
                ],
                vertical=True,
                pills=True,
                className="nav nav-link:hover",
            ),
            html.Div(
                [
                    dbc.Row(
                        dbc.Col(
                            html.Div("Copyright © 2021", style={"font-size": "0.8rem"}),
                            style={
                                "right": "-10px",
                                "bottom": "-600px",
                                "width": "100%",
                                # "height": "100%",
                                # "object-fit": "cover",
                            },
                        ),
                        style={"position": "absolute"},
                    ),
                ]
            ),
        ],
        style=SIDEBAR_STYLE,
    )
    return sidebar


def home_page():
    home_content = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(html.Div(navigation_bar()), width=2),
                    dbc.Col([html.Br(), html.Div(home.home_layout)], width=10),
                ]
            )
        ],
        fluid=True,
    )
    return home_content


def content_eda():
    content_1 = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(html.Div(navigation_bar()), width=2),
                    dbc.Col([html.Br(), html.Div(analytics.a_layout)], width=10),
                ]
            )
        ],
        fluid=True,
    )
    return content_1


def content_cluster():
    content_2 = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(html.Div(navigation_bar()), width=2),
                    dbc.Col([html.Br(), html.Div(clustering.c_layout)], width=10),
                ]
            )
        ],
        fluid=True,
    )
    return content_2


def about_page():
    about_content = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(html.Div(navigation_bar()), width=2),
                    dbc.Col([html.Br(), html.Div(about.about_layout)], width=10),
                ]
            )
        ],
        fluid=True,
    )
    return about_content