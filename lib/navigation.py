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


# Function for calling navigation bar
def navigation_bar():
    sidebar = html.Div(
        [
            dbc.Button(
                [html.Img(src=KIWI_LOGO, className="nav-img")],
                href=kiwibot,
                color="None",
                block=True,
            ),
            dbc.Nav(
                [
                    dbc.NavLink(
                        "Home",
                        href="/home",
                        # active=True,
                        className="nav-link",
                    ),
                    dbc.NavLink(
                        "Descriptive Analytics",
                        href="/analytics",
                        # active=True,
                        className="nav-link",
                    ),
                    dbc.NavLink(
                        "Clustering Analytics",
                        href="/clustering",
                        # active=True,
                        className="nav-link",
                    ),
                    dbc.NavLink(
                        "About Us",
                        href="/about",
                        # active=True,
                        className="nav-link:hover",
                    ),
                ],
                vertical=True,
                pills=True,
            ),
            html.Div(
                [
                    dbc.Row(
                        dbc.Col(
                            html.Div("Copyright © 2021", className="copyright-text"),
                            className="copyright-col",
                        ),
                        className="copyright-row",
                    ),
                ]
            ),
        ],
        className="sidebar-nav",
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