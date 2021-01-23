import os
import pathlib

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
import plotly.graph_objs as go
from dash.dependencies import ClientsideFunction, Input, Output, State
from dash.exceptions import PreventUpdate
from sklearn import datasets
from sklearn.cluster import KMeans

from lib import navigation

from .data_engine.preprocessor import dfkiwer, dforder

app = __import__("app").app


layout_1 = dbc.Container(
    [
        html.H1("Descriptive Reporting", style={"color": "#000000"}),
    ],
    fluid=True,
)

# tab_1 contains the alert messages and the plots from kiwers
tab1_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(
                [
                    dbc.Button(
                        "More Info", id="alert-toggle-no-fade", className="mr-1"
                    ),
                    html.Hr(),
                    dbc.Alert(
                        "Select the type of chart you want to analyse",
                        id="alert-no-fade",
                        dismissable=True,
                        is_open=True,
                    ),
                ]
            ),
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    "insert KIWERS plots here",
                                    style={"color": "#000000"},
                                )
                            )
                        ],
                        align="start",
                    ),
                ],
            ),
        ],
    ),
    className="mt-3",
)

# tab_2 contains the alert messages and the plots from orders
tab2_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(
                [
                    dbc.Button("More Info", id="alert-toggle-fade", className="mr-1"),
                    html.Hr(),
                    dbc.Alert(
                        "Select the type of chart you want to analyse",
                        id="alert-fade",
                        dismissable=True,
                        fade=False,
                        duration=4000,
                    ),
                ]
            ),
            dbc.Container(
                [
                    dbc.Row(
                        [dbc.Col(html.Div("insert plots here"))],
                        align="start",
                    ),
                ],
            ),
        ]
    ),
    className="mt-3",
)

# Component to call dashboard in tabs
analytics_tab = dbc.Tabs(
    [
        dbc.Tab(tab1_content, label="Kiwers"),
        dbc.Tab(tab2_content, label="Orders"),
    ]
)


@app.callback(
    Output("alert-fade", "is_open"),
    [Input("alert-toggle-fade", "n_clicks")],
    [State("alert-fade", "is_open")],
)
def toggle_alert(n, is_open):
    if n:
        return not is_open
    return is_open


# Callback function for message info
@app.callback(
    Output("alert-no-fade", "is_open"),
    [Input("alert-toggle-no-fade", "n_clicks")],
    [State("alert-no-fade", "is_open")],
)
def toggle_alert_no_fade(n, is_open):
    if n:
        return not is_open
    return is_open


a_layout = html.Div([layout_1, analytics_tab])