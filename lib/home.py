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
                                            className="home-title",
                                        ),
                                        html.H4(
                                            "KAD is a tool for get comprehensive analytics about kiwibot\
                                                business and create strategies for supply the demand of kiwibots\
                                                    in key areas based in a cluster prediction of hot spot zones.\
                                                        To use this tool select in the navigation bar the ",
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
