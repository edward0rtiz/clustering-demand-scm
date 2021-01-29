import os
import pathlib
import time

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
from lib.analytics_kiwers import kiwers_layout
from lib.analytics_orders import orders_layout

from .data_engine.preprocessor import dfkiwer, dforder

app = __import__("app").app

more_info_text = "In this section you will find different plots to track the evolution\
 of logins by kiwers and the login points by market."

more_info_text_2 = " In this section you will get detail information about the orders\
 and, resturants, clients. This insights will serve the team to get more information to\
 create action plans in the marketing department."

layout_1 = dbc.Container(
    [
        html.Div(
            children=[
                html.Div(
                    dcc.Loading(
                        id="input-2",
                        children=[html.Div(id="output-2")],
                        type="default",
                        color="#000000",
                        fullscreen=True,
                    )
                ),
                html.H1("Descriptive Reporting"),
            ]
        ),
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
                        "More Info",
                        id="collapse-button",
                        className="mr-1",
                        color="dark",
                        outline=True,
                    ),
                    html.Hr(),
                    dbc.Collapse(
                        dbc.Card(
                            dbc.CardBody(more_info_text, className="card-analytics"),
                        ),
                        id="collapse",
                    ),
                ]
            ),
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    kiwers_layout,
                                    className="layout-text",
                                )
                            ),
                        ],
                        align="start",
                    ),
                ],
                fluid=True,
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
                    dbc.Button(
                        "More Info",
                        id="collapse-button-2",
                        className="mr-1",
                        color="dark",
                        outline=True,
                    ),
                    html.Hr(),
                    dbc.Collapse(
                        dbc.Card(
                            dbc.CardBody(more_info_text_2, className="card-analytics"),
                        ),
                        id="collapse-2",
                    ),
                ]
            ),
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    orders_layout,
                                    className="layout-text",
                                ),
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

# Component to call dashboard in tabs
analytics_tab = dbc.Tabs(
    [
        dbc.Tab(tab1_content, label="Kiwers"),
        dbc.Tab(tab2_content, label="Orders"),
    ]
)


@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse-2", "is_open"),
    [Input("collapse-button-2", "n_clicks")],
    [State("collapse-2", "is_open")],
)
def toggle_collapse_2(n, is_open):
    if n:
        return not is_open
    return is_open


a_layout = html.Div([layout_1, analytics_tab])


@app.callback(Output("output-2", "children"), [Input("input-2", "value")])
def input_triggers_spinner2(value):
    time.sleep(3)
    return value
