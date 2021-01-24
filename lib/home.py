import os
import pathlib

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html


SRC_VIDEO = "https://bit.ly/3o6VBuc"
home_layout = dbc.Container(
    [
        dbc.Row(
            [
                html.Div(
                    [
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        html.H1(
                                            "Kiwibot Analytical Dashboard",
                                            style={
                                                "color": "#000000",
                                                "font-size": "50px",
                                                "line-height": "40px",
                                                "letter-spacing": "-2px",
                                            },
                                        ),
                                        html.H4(
                                            "Kiwibot Analytical Dashboard",
                                            style={
                                                "color": "#000000",
                                                "font-size": "18px",
                                                "line-height": "40px",
                                                "letter-spacing": "-2px",
                                            },
                                        ),
                                    ],
                                    style={
                                        "width": "100%",
                                        "margin-top": "100px",
                                        "margin-bottom": "-40px",
                                        # "font-size": "50px",
                                        # "line-height": "100px",
                                        # "letter-spacing": "-2px",
                                    },
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
                                        #     "right": "-100%",
                                        # "bottom": "-100%",
                                        "top": "200%",
                                        "left": "-0.6%",
                                        "object-fit": "cover",
                                        "z-index": -100,
                                    },
                                ),
                            ],
                            width=30,
                        )
                    ]
                )
            ]
        ),
    ],
    fluid=True,
)
