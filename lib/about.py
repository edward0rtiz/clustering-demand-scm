import os
import pathlib

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from app import app


EMAIL_LOGO = "../assets/email.png"
carloslink = "https://www.linkedin.com/in/carlos-molano-salazar/"
edwardlink = "https://www.linkedin.com/in/ortizedward/"

# Layout of main components
about_layout = dbc.Container(
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
                                            "Meet the team",
                                            style={
                                                "color": "#000000",
                                                "font-size": "50px",
                                                "line-height": "40px",
                                                "letter-spacing": "-2px",
                                            },
                                        ),
                                        html.H4(
                                            "behind this awesome dashboard",
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
                                dbc.Container(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.Img(
                                                            src=app.get_asset_url(
                                                                "kiwibot-carlos.jpg"
                                                            ),
                                                            height="250px",
                                                            className="img_marg",
                                                        ),
                                                        html.H5(
                                                            "Carlos Molano",
                                                            className="H5_margin",
                                                        ),
                                                        html.P(
                                                            "Mechanic Engineer | SWE - ML",
                                                            className="P_margin",
                                                        ),
                                                        dbc.Button(
                                                            [
                                                                html.Img(
                                                                    src=EMAIL_LOGO,
                                                                    height="24px",
                                                                    className="logo_correo",
                                                                )
                                                            ],
                                                            color="secondary",
                                                            className="correo_marg",
                                                            href="mailto:cmmolanos@gmail.com",
                                                        ),
                                                        dbc.Button(
                                                            "in",
                                                            size="lg",
                                                            color="secondary",
                                                            className="In_marg",
                                                            href=carloslink,
                                                        ),
                                                    ],
                                                    width=4,
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.Img(
                                                            src=app.get_asset_url(
                                                                "edward.png"
                                                            ),
                                                            height="250px",
                                                            className="img_marg",
                                                        ),
                                                        html.H5(
                                                            "Edward Ortiz",
                                                            className="H5_margin",
                                                        ),
                                                        html.P(
                                                            "Product Manager | SWE - ML |",
                                                            className="P_margin",
                                                        ),
                                                        dbc.Button(
                                                            [
                                                                html.Img(
                                                                    src=EMAIL_LOGO,
                                                                    height="24px",
                                                                    className="logo_correo",
                                                                )
                                                            ],
                                                            color="secondary",
                                                            className="correo_marg",
                                                            href="mailto:edwardarmandoortiz@gmail.com",
                                                        ),
                                                        dbc.Button(
                                                            "in",
                                                            size="lg",
                                                            color="secondary",
                                                            className="In_marg",
                                                            href=edwardlink,
                                                        ),
                                                    ],
                                                    width=4,
                                                ),
                                            ],
                                            justify="between",
                                            className="container-profile",
                                        ),
                                    ]
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