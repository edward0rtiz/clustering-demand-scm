import os
import pathlib

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import time

app = __import__("app").app


SRC_VIDEO = "https://bit.ly/3o6VBuc"
home_layout = dbc.Container(
    [
        dbc.Row(
            [
                html.Div(
                    children=[
                        html.Div(
                            dcc.Loading(
                                id="input-1",
                                children=[html.Div(id="output-1")],
                                type="default",
                                color="#000000",
                                fullscreen=True,
                            ),
                        ),
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        html.H1(
                                            "Kiwibot Analytical Dashboard",
                                            className="home-title",
                                        ),
                                        html.H4("KAD is a tool for get comprehensive analytics about kiwibot\
                                                business and create strategies for supply the demand of kiwibots\
                                                in key areas based in a cluster prediction of hot spot zones.\
                                                To use this tool select in the navigation bar the insights you want\
                                                to explore and get the information updated in real-time.\
                                                If you want to download a report based on the insights gathered\
                                                click in the button below",
                                            className="home-subtitle",
                                        ),
                                    ],
                                    className="home-main",
                                ),
                                html.Video(
                                    src=SRC_VIDEO,
                                    autoPlay="autoplay",
                                    loop="loop",
                                    style={
                                        "background-size": "cover",
                                        "background-position": "50% 50%",
                                        "position": "absolute",
                                        "margin": "auto",
                                        "width": "100%",
                                        "height": "-80%",
                                        "top": "200%",
                                        "left": "-0.6%",
                                        "object-fit": "cover",
                                        "z-index": -100,
                                    },
                                ),
                            ],
                            width=30,
                        ),
                    ],
                )
            ]
        ),
    ],
    fluid=True,
)


@app.callback(Output("output-1", "children"), [Input("input-1", "value")])
def input_triggers_spinner(value):
    time.sleep(2)
    return value