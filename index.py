# Basics Requirements
import pandas as pd
import pathlib
import os
import dash
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px

# Dash Bootstrap Components
import dash_bootstrap_components as dbc

# Recall app
from app import app, server

###########################################################
#
#           APP LAYOUT:
#
###########################################################

# Import components
from lib import navigation

# Variables of static files
KIWI_LOGO = "../static/logo2.png"

# hypelinks
kiwibot = "https://www.kiwibot.com/"

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "height": "100vh",
    "margin-left": "10rem",
    # "margin-right": "0rem",
    # "margin-bottom": "150rem",
    # "padding": "20rem 2rem",
    "background-color": "#FFFFFF",
}
# Main layout: contains the main layot with multiple pages

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        navigation.navigation_bar(),
        content
    ])

###############################################
#
#           PAGES INTERACTIVITY:
#
###############################################


###############################################
#           APP INTERACTIVITY:
#
###############################################
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/analytics":
        return html.P("This is the content of the home page!")
    elif pathname == "/clustering":
        return html.P("This is the content of page 1. Yay!")
    elif pathname == "/about":
        return html.P("Oh cool, this is page 2!")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == "__main__":
    app.run_server(debug=True)
