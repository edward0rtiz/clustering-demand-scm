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

from lib.analytics_kiwers import kiwers_layout

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
                        "More Info",
                        id="collapse-button",
                        className="mr-1",
                        color="dark",
                        outline=True,
                    ),
                    html.Hr(),
                    dbc.Collapse(
                        dbc.Card(
                            dbc.CardBody(more_info_text, style={"color": "black"}),

                        ),
                        id="collapse"
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
                                    style={"color": "#000000"},
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
    Output("alert-fade", "is_open"),
    [Input("alert-toggle-fade", "n_clicks")],
    [State("alert-fade", "is_open")],
)
def toggle_alert(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


a_layout = html.Div([layout_1, analytics_tab])
