import os
import pathlib

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import ClientsideFunction, Input, Output, State
from dash.exceptions import PreventUpdate
from sklearn import datasets
from sklearn.cluster import KMeans

from lib import navigation

from .data_engine.preprocessor import dfkiwer, dforder

app = __import__("app").app


layout_2 = dbc.Container(
    [
        html.H1("Clustering Reporting", style={"color": "#000000"}),
    ],
    fluid=True,
)

tab_c1_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(
                [
                    dbc.Button(
                        "More Info", id="alert-toggle-no-fade-2", className="mr-1"
                    ),
                    html.Hr(),
                    dbc.Alert(
                        "Select the type of chart you want to analyse",
                        id="alert-no-fade-2",
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
                                    "insert KIWERS CLUSTplots here",
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


tab_c2_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(
                [
                    dbc.Button("More Info", id="alert-toggle-fade-2", className="mr-1"),
                    html.Hr(),
                    dbc.Alert(
                        "Select the type of chart you want to analyse",
                        id="alert-fade-2",
                        dismissable=True,
                        fade=False,
                        duration=4000,
                    ),
                ]
            ),
            dbc.Container(
                [
                    dbc.Row(
                        [dbc.Col(html.Div("insert ORDERS CLUSTplots here"))],
                        align="start",
                    ),
                ],
            ),
        ]
    ),
    className="mt-3",
)


# Component to call dashboard in tabs
clustering_tab = dbc.Tabs(
    [
        dbc.Tab(tab_c1_content, label="Cluster Continuous"),
        dbc.Tab(tab_c2_content, label="Cluster Categorical"),
    ]
)


@app.callback(
    Output("alert-fade-2", "is_open"),
    [Input("alert-toggle-fade-2", "n_clicks")],
    [State("alert-fade-2", "is_open")],
)
def toggle_alert_2(n, is_open):
    if n:
        return not is_open
    return is_open


# Callback function for message info
@app.callback(
    Output("alert-no-fade-2", "is_open"),
    [Input("alert-toggle-no-fade-2", "n_clicks")],
    [State("alert-no-fade-2", "is_open")],
)
def toggle_alert_no_fade_2(n, is_open):
    if n:
        return not is_open
    return is_open


c_layout = html.Div([layout_2, clustering_tab])