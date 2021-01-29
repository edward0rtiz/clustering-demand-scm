import dash
from dash.dependencies import Input, Output

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

import plotly.express as px

import pandas as pd

from lib.data_engine.preprocessor import (map_neighborhood,
                                          map_city_clusters,
                                          berkeley_merge)

app = __import__("app").app

############################ Layout ################################################

cluster_foursquare = [
    dbc.Row(dbc.Col(html.H3('Foursquare'))),
    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    dcc.Graph(figure=map_neighborhood),
                    className="div-style"
                ),
                width=6
            ),
            dbc.Col(
                html.Div(
                    dcc.Graph(figure=map_city_clusters),
                    className="div-style"
                ),
                width=6
            ),
        ]
    ),
    dbc.Row(dbc.Col(html.Br())),
    dbc.Row(dbc.Col(html.H3('Top 10 Restaurants by Neighborhood'))),
    dbc.Row(
        dbc.Col(
            html.Div(

                dbc.Table.from_dataframe(berkeley_merge[berkeley_merge.columns[1:]],
                                         striped=True,
                                         bordered=True,
                                         hover=True,
                                         responsive=True)
            )
        ),
    )
]

