import os
import pathlib

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import ClientsideFunction, Input, Output, State
from dash.exceptions import PreventUpdate

from app import app, server
from lib import navigation

# APP LAYOUT:
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        navigation.navigation_bar(),
        html.Div(id="page-content"),
    ]
)

# APP INTERACTIVITY:
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if (pathname == "/") or (pathname == "/home"):
        return navigation.home_page()
    if (pathname == "/analytics") or (pathname == "/"):
        return navigation.content_eda()
    if pathname == "/clustering":
        return navigation.content_cluster()
    elif pathname == "/about":
        return navigation.about_page()


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)
