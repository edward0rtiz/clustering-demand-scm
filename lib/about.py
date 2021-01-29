import os
import pathlib

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import time
app = __import__("app").app

EMAIL_LOGO = "../assets/email.png"
carloslink = "https://www.linkedin.com/in/carlos-molano-salazar/"
edwardlink = "https://www.linkedin.com/in/ortizedward/"

# Layout of main components
about_layout = dbc.Container(
    [
        dbc.Row(
            [
                html.Div(
                    children=[
                        html.Div(
                            dcc.Loading(
                                id="home-input-1",
                                children=[html.Div(id="home-output-1")],
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
                                            "Meet the team",
                                            className="about-title",
                                        ),
                                        html.H4("behind this awesome dashboard",
                                            className="about-subtitle",
                                        ),
                                    ],
                                    className="home-main",
                                ),
                            ],
                            width=12,
                        ),
                    ],
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Img(
                            src=app.get_asset_url(
                                    "kiwibot-carlos.jpg"
                                ),
                        height="250px",
                        className="img-marg",
                        ),
                        html.H5("Carlos Molano",className="H5-margin"),
                        html.P("Mechanic Engineer | SWE - ML",
                            className="P-margin",
                        ),
                        dbc.ButtonGroup(
                            [
                                dbc.Button(
                                    [
                                        html.Img(
                                            src=EMAIL_LOGO,
                                            height="24px",
                                            className="icon-mail",
                                        )
                                    ],
                                    outline=True,
                                    color="dark",
                                    className="mail-marg",
                                    href="mailto:cmmolanos@gmail.com",
                                ),
                                dbc.Button(
                                    "in",
                                    size="lg",
                                    color="dark",
                                    className="In-marg",
                                    href=carloslink,
                                ),
                            ], className="button-margin"
                        )
                    ], className="social-margin"
                ),
                dbc.Col(
                    [
                        html.Img(
                            src=app.get_asset_url(
                                "edward.png"
                        ),
                        height="250px",
                        className="img-marg",
                        ),
                        html.H5("Edward Ortiz",className="H5-margin"),
                        html.P("Product Manager | SWE - ML",
                                className="P-margin",
                        ),
                        dbc.ButtonGroup(
                            [
                                dbc.Button(
                                    [
                                        html.Img(
                                            src=EMAIL_LOGO,
                                            height="24px",
                                            className="icon-mail",
                                        )
                                    ],
                                    outline=True,
                                    color="dark",
                                    className="mail-marg",
                                    href="mailto:edwardarmandoortiz@gmail.com",
                                ),
                                dbc.Button(
                                    "in",
                                    size="lg",
                                    color="dark",
                                    className="In-marg",
                                    href=edwardlink,
                                ), 
                            ], className="button-margin-2"
                        ),                         
                    ], className="social-margin-2"
                ),
            ], className="row-margin"
        ),
    ], fluid=True    
)   #     className="container-profile responsive",



@app.callback(Output("home-output-1", "children"), [Input("home-input-1", "value")])
def input_triggers_spinner_home(value):
    time.sleep(1)
    return value
