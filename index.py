# Basics Requirements
import pandas as pd
import pathlib
import os
import dash
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px

# Dash Bootstrap Components
import dash_bootstrap_components as dbc

# Recall app
from app import app, server

###########################################################
#
#           APP LAYOUT:
#
###########################################################

# Import components
from lib import navigation

# Variables of static files
KIWI_LOGO = "../static/logo2.png"

# hypelinks
kiwibot = "https://www.kiwibot.com/"

# Main layout: contains the main layot with multiple pages

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        navigation.navbar(),
        html.Div(id="page-content"),
        html.Div(
            [
                dbc.Alert(
                    [
                        dbc.Row(
                            [
                                dbc.Button(
                                    [html.Img(src=KIWI_LOGO, height="20px")],
                                    active=True,
                                    href=kiwibot,
                                    color="#000000",
                                    className="bottom_logo",
                                ),
                            ]
                        ),
                    ],
                    className="bottom_bar",
                ),
            ]
        ),
    ]
)

###############################################
#
#           PAGES INTERACTIVITY:
#
###############################################


###############################################
#           APP INTERACTIVITY:
#
###############################################


if __name__ == "__main__":
    app.run_server(debug=True)
