import dash
from dash.dependencies import Input, Output

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

import plotly.express as px

from lib.data_engine.preprocessor import (
    dfkiwer_dates,
    dfkiwer_hours,
    dfkiwer_days,
    dfkiwer_month,
    dfkiwer_weeks,
    kiwer_map,
    multiple_weekday,
    kiwers_dayxw,
    kiwers_hxm,
)

app = __import__("app").app

# Radios components
radios_line_k = dbc.FormGroup(
    [
        dbc.Label("Total Logs", html_for="example-radios-row", width=4),
        dbc.Col(
            dbc.RadioItems(
                id="chart-type-line-k",
                options=[
                    {"label": "By date", "value": "By date"},
                    {"label": "By days", "value": "By days"},
                    {"label": "By hours", "value": "By hours"},
                ],
                value="By date",
                labelStyle={
                    "display": "inline-block",
                    "padding": "12px 12px 12px 0px",
                },
            ),
            width=8,
        ),
    ],
    row=True,
)

radios_evo_k = dbc.FormGroup(
    [
        dbc.Label("Evolutions", html_for="example-radios-row", width=4),
        dbc.Col(
            dbc.RadioItems(
                id="chart-type-evo-k",
                options=[
                    {"label": "Weekday by month", "value": "Weekday by month"},
                    {"label": "Hour by month", "value": "Hour by month"},
                    {"label": "Month by hour", "value": "Month by hour"},
                    {"label": "Day by weeks", "value": "Day by weeks"},
                ],
                value="Weekday by month",
            ),
            width=8,
        ),
    ],
    row=True,
)
radios_bar_k = dbc.FormGroup(
    [
        dbc.Label("Logs", html_for="example-radios-row", width=4),
        dbc.Col(
            dbc.RadioItems(
                id="chart-type-bar-k",
                options=[
                    {"label": "By month", "value": "By month"},
                    {"label": "By week", "value": "By week"},
                ],
                value="By month",
            ),
            width=8,
        ),
    ],
    row=True,
)

kiwers_layout = [
    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    radios_line_k,
                    className="div-style-kiwer",
                ),
                md=4,
            ),
            dbc.Col(
                html.Div(
                    dcc.Graph(id="plot-line-k"),
                    className="div-style-plot",
                ),
                md=8,
            ),
        ],
        align="center",
    ),
    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    radios_evo_k,
                    className="div-style-kiwer",
                ),
                md=4,
            ),
            dbc.Col(
                html.Div(
                    dcc.Graph(id="plot-evo-k"),
                    className="div-style-plot",
                ),
                md=8,
            ),
        ],
        align="center",
    ),
    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    radios_bar_k,
                    className="div-style-kiwer",
                ),
                md=4,
            ),
            dbc.Col(
                html.Div(
                    dcc.Graph(id="plot-bar-k"),
                    className="div-style-plot",
                ),
                md=8,
            ),
        ],
        align="center",
    ),
    dbc.Row(dbc.Col(html.H3("Log Points"))),
    dbc.Row(dbc.Col(dcc.Graph(figure=kiwer_map))),
]


# Callback for line
@app.callback(
    Output("plot-line-k", "figure"),
    Input("chart-type-line-k", "value"),
)
def update_output(chart_type):
    plots = {
        "By date": {
            "df": dfkiwer_dates,
            "x": "Date",
            "y": "Logs",
            "title": "Total Logs by date",
        },
        "By days": {
            "df": dfkiwer_days,
            "x": "Weekday",
            "y": "Logs",
            "title": "Total Logs by day",
        },
        "By hours": {
            "df": dfkiwer_hours,
            "x": "Hour",
            "y": "Logs",
            "title": "Total Logs by hour",
        },
    }

    fig = px.line(
        plots[chart_type]["df"],
        x=plots[chart_type]["x"],
        y=plots[chart_type]["y"],
        title=plots[chart_type]["title"],
        height=400,
    )
    fig.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
        }
    )
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="LightGrey",
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="LightGrey",
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="LightGrey",
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="LightGrey",
    )
    return fig


# Callback for evolution plot
@app.callback(
    Output("plot-evo-k", "figure"),
    Input("chart-type-evo-k", "value"),
)
def update_output(chart_type):
    plots = {
        "Weekday by month": {
            "df": multiple_weekday,
            "x": "month",
            "y": "username",
            "color": "weekday",
            "labels": {"weekday": "weekday", "username": "log", "month": "month"},
            "title": "Evolution of weekday",
        },
        "Hour by month": {
            "df": kiwers_hxm,
            "x": "month",
            "y": "username",
            "color": "hour",
            "labels": {"weekday": "weekday", "username": "log", "hour": "hour"},
            "title": "Evolution of each hour by month",
        },
        "Month by hour": {
            "df": kiwers_hxm,
            "x": "hour",
            "y": "username",
            "color": "month",
            "labels": {"weekday": "weekday", "username": "log", "hour": "hour"},
            "title": "Evolution of month by hour",
        },
        "Day by weeks": {
            "df": kiwers_dayxw,
            "x": "week",
            "y": "username",
            "color": "weekday",
            "labels": {"weekday": "weekday", "username": "log", "week": "week"},
            "title": "Evolution of day by weeks",
        },
    }
    fig = px.line(
        plots[chart_type]["df"],
        x=plots[chart_type]["x"],
        y=plots[chart_type]["y"],
        color=plots[chart_type]["color"],
        labels=plots[chart_type]["labels"],
        title=plots[chart_type]["title"],
        height=400,
    )
    fig.update_traces(hoverinfo="text+name", mode="lines+markers")
    fig.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
        }
    )
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="LightGrey",
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="LightGrey",
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="LightGrey",
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="LightGrey",
    )
    return fig


# Callback for barplot
@app.callback(
    Output("plot-bar-k", "figure"),
    Input("chart-type-bar-k", "value"),
)
def update_output(chart_type):
    plots = {
        "By month": {
            "df": dfkiwer_month,
            "x": "Month",
            "y": "Logs",
            "title": "Logs by month",
        },
        "By week": {
            "df": dfkiwer_weeks,
            "x": "Week",
            "y": "Logs",
            "title": "Logs by week",
        },
    }

    fig = px.bar(
        plots[chart_type]["df"],
        x=plots[chart_type]["x"],
        y=plots[chart_type]["y"],
        title=plots[chart_type]["title"],
        height=400,
    )
    fig.update_layout(
        {
            "plot_bgcolor": "rgba(0, 0, 0, 0)",
            "paper_bgcolor": "rgba(0, 0, 0, 0)",
        }
    )
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="LightGrey",
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="LightGrey",
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="LightGrey",
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor="LightGrey",
    )

    return fig
