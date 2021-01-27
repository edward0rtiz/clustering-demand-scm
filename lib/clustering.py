import os
import pathlib
import time

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
from lib.cluster_orders_continous import cluster_orders_layout

from .data_engine.preprocessor import dfkiwer, dforder

app = __import__("app").app


more_info_text = """Lorem Ipsum is simply dummy text of the printing and 
typesetting industry. Lorem Ipsum has been the industry's standard dummy 
text ever since the 1500s, when an unknown printer took a galley of type 
and scrambled it to make a type specimen book. It has survived not only 
five centuries, but also the leap into electronic typesetting, remaining 
essentially unchanged. It was popularised in the 1960s with the release 
of Letraset sheets containing Lorem Ipsum passages, and more recently with 
desktop publishing software like Aldus PageMaker including versions of Lorem 
Ipsum"""

layout_2 = dbc.Container(
    [
        html.Div(
            children=[
                html.Div(
                    dcc.Loading(
                        id="input-3",
                        children=[html.Div(id="output-3")],
                        type="default",
                        color="#000000",
                        fullscreen=True,
                    )
                ),
                html.H1("Clustering Reporting"),
            ]
        ),
    ],
    fluid=True,
)

tab_c1_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(
                [
                    dbc.Button(
                        "More Info",
                        id="collapse-button-3",
                        className="mr-1",
                        color="dark",
                        outline=True,
                    ),
                    html.Hr(),
                    dbc.Collapse(
                        dbc.Card(
                            dbc.CardBody(more_info_text, className="card-analytics"),
                        ),
                        id="collapse-3",
                    ),
                ]
            ),
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    cluster_orders_layout,
                                    className="layout-text",
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
                    dbc.Button(
                        "More Info",
                        id="collapse-button-4",
                        className="mr-1",
                        color="dark",
                        outline=True,
                    ),
                    html.Hr(),
                    dbc.Collapse(
                        dbc.Card(
                            dbc.CardBody(more_info_text, className="card-analytics"),
                        ),
                        id="collapse-4",
                    ),
                ]
            ),
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    "insert ORDERS CLUSTplots here",
                                    className="layout-text",
                                )
                            )
                        ],
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
    Output("collapse-3", "is_open"),
    [Input("collapse-button-3", "n_clicks")],
    [State("collapse-3", "is_open")],
)
def toggle_collapse3(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse-4", "is_open"),
    [Input("collapse-button-4", "n_clicks")],
    [State("collapse-4", "is_open")],
)
def toggle_collapse_4(n, is_open):
    if n:
        return not is_open
    return is_open


c_layout = html.Div([layout_2, clustering_tab])


@app.callback(Output("output-3", "children"), [Input("input-3", "value")])
def input_triggers_spinner3(value):
    time.sleep(3)
    return value
