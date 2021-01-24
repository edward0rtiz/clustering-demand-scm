import dash
from dash.dependencies import Input, Output

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

import plotly.express as px

from lib.data_engine.preprocessor import (bots_busiest_day,
                                          boxplot_cost,
                                          client_count_plot,
                                          dforder_dates,
                                          dforder_days,
                                          dforder_hours,
                                          dforder_hourxm,
                                          dforder_weeks,
                                          dforder_xm,
                                          heatmap_1,
                                          heatmap_2,
                                          parallel,
                                          restaurant_summary,
                                          tips_hour,
                                          totalcost_byweek,
                                          type_plot)

app = __import__("app").app

########################## Radios components ###############################
radios_orders_o = dbc.FormGroup(
    [
        dbc.Label("Orders", html_for="example-radios-row", width=4),
        dbc.Col(
            dbc.RadioItems(
                id="chart-type-orders-o",
                options=[
                    {"label": "By weeks", "value": "By weeks"},
                    {"label": "By days", "value": "By days"},
                    {"label": "By hours", "value": "By hours"}
                ],
                value="By weeks",
                inline=True,
            ),
            width=8,
        ),
    ],
    row=True,
)

radios_evolutions_o = dbc.FormGroup(
    [
        dbc.Label("Evolutions", html_for="example-radios-row", width=4),
        dbc.Col(
            dbc.RadioItems(
                id="chart-type-evo-o",
                options=[
                    {"label": "weekday", "value": "weekday"},
                    {"label": "monthly", "value": "monthly"},
                    {"label": "hours", "value": "hours"}
                ],
                value="weekday",
                inline=True,
            ),
            width=8,
        ),
    ],
    row=True,
)

div_style = {"border": "1px solid lightgrey",
             "borderRadius": "5px",
             "backgroundColor": "#F9F9F9",
             "margin": "5px",
             # "padding": "26px 0px 0px 30px",
             "boxShadow": "2px 2px 2px lightgrey",
             }
div_style_radios = {"border": "1px solid lightgrey",
                    "borderRadius": "5px",
                    "backgroundColor": "#F9F9F9",
                    "margin": "5px",
                    "padding": "5px 0px 0px 5px",
                    "boxShadow": "2px 2px 2px lightgrey",
                    "width": "600px"
                    }

orders_layout = [
    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    dcc.Graph(figure=parallel),
                    style=div_style,
                ),
                width=6,
            ),
            dbc.Col(
                [
                    dbc.Row(
                        dbc.Col(
                            html.Div(
                                dcc.Graph(figure=type_plot),
                                style=div_style
                            ),
                        ),
                    ),
                    dbc.Row(
                        dbc.Col(
                            html.Div(
                                dcc.Graph(figure=client_count_plot),
                                style=div_style,
                            )
                        ),
                    ),
                ],
                width=6
            ),
        ],
    ),
    dbc.Row(dbc.Col(html.H3("Correlation"))),
    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    dcc.Graph(figure=heatmap_1),
                    style=div_style,
                ),
                width=6,
            ),

            dbc.Col(
                html.Div(
                    dcc.Graph(figure=heatmap_2),
                    style=div_style,
                ),
                width=6,
            ),
        ]
    ),
    dbc.Row(dbc.Col(html.H3("Order Facts"))),
    dbc.Row(
        [
            dbc.Col(
                [
                    dcc.DatePickerRange(
                        id="plot-date-picker-o",
                        start_date=dforder_dates.index.min(),
                        end_date=dforder_dates.index.max(),
                        min_date_allowed=dforder_dates.index.min(),
                        max_date_allowed=dforder_dates.index.max()
                    )
                ]
            )
        ]
    ),
    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    dcc.Graph(id="plot-date-o"),
                ),
                style=div_style,
            ),
        ]
    ),
    dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Row(
                        dbc.Col(
                            html.Div(
                                radios_orders_o,
                                style=div_style,
                            ),
                        ),
                    ),
                    dbc.Row(
                        dbc.Col(
                            html.Div(
                                dcc.Graph(id="plot-orders-o"),
                                style=div_style,
                            ),
                        )
                    )
                ],
                md=6,
            ),
            dbc.Col(
                [
                    dbc.Row(
                        dbc.Col(
                            html.Div(
                                radios_evolutions_o,
                                style=div_style,
                            ),
                        ),
                    ),
                    dbc.Row(
                        dbc.Col(
                            html.Div(
                                dcc.Graph(id="plot-evo-o"),
                                style=div_style,
                            ),
                        ),
                    )
                ],
                md=6,
            ),
        ],
        #      align="center"
    ),
    dbc.Row(
        [
            dbc.Col(
                html.Div(dcc.Graph(figure=boxplot_cost), style=div_style),

            ),
            dbc.Col(
                html.Div(dcc.Graph(figure=totalcost_byweek), style=div_style),

            ),
        ]
    ),
    dbc.Row(
        [
            dbc.Col(
                html.Div(
                    dcc.Graph(figure=tips_hour),
                    style=div_style,
                ),
                width=6,
            ),
            dbc.Col(
                html.Div(
                    dcc.Graph(figure=bots_busiest_day),
                    style=div_style,
                ),
                width=6,
            ),
        ],
    ),
    dbc.Row(dbc.Col(html.Div(dcc.Graph(figure=restaurant_summary), style=div_style)))
]


# Callback update Orders by date range
@app.callback(
    Output("plot-date-o", "figure"),
    [Input('plot-date-picker-o', 'start_date'),
     Input('plot-date-picker-o', 'end_date')]
)
def update_plot(start_date, end_date):
    """Re subset the dataframe and plot with the new range.

    Args:
        start_date (date): start date
        end_date (date): end date

    Returns:
        the fig with the updated plot
    """
    df_new_range = dforder_dates[start_date:end_date]
    fig = px.line(df_new_range,
                  x=df_new_range.index,
                  y="orders",
                  title='Orders by date range',
                  labels=dict(x="Date", orders="Orders")
                  )
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                       'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey',
                     zeroline=True, zerolinewidth=2, zerolinecolor='LightGrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey',
                     zeroline=True, zerolinewidth=2, zerolinecolor='LightGrey')

    return fig


# Callback for orderscount
@app.callback(
    Output("plot-orders-o", "figure"),
    Input("chart-type-orders-o", "value"),
)
def update_output(chart_type):
    plots = {'By weeks': {'df': dforder_weeks,
                          'x': dforder_weeks.index,
                          "y": "orders",
                          "title": "Orders by week",
                          "labels": dict(x="Weeks", orders='Orders')},
             'By days': {'df': dforder_days,
                         'x': "Weekday",
                         "y": "Orders",
                         "title": "Orders by day",
                         "labels": None},
             'By hours': {'df': dforder_hours,
                          'x': "Hour",
                          "y": "Orders",
                          "title": "Orders by hour",
                          "labels": None},
             }

    fig = px.bar(plots[chart_type]['df'],
                 x=plots[chart_type]['x'],
                 y=plots[chart_type]['y'],
                 title=plots[chart_type]['title'],
                 labels=plots[chart_type]['labels'],
                 height=400,
                 )
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                       'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey',
                     zeroline=True, zerolinewidth=2, zerolinecolor='LightGrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey',
                     zeroline=True, zerolinewidth=2, zerolinecolor='LightGrey')

    return fig


# Callback for evolutions
@app.callback(
    Output("plot-evo-o", "figure"),
    Input("chart-type-evo-o", "value"),
)
def update_output(chart_type):
    plots = {'weekday': {'df': dforder_xm,
                         'x': 'month',
                         "y": 'order_id',
                         "color": "weekday",
                         "title": "Evolution of Weekday-Orders by month",
                         "labels": {'month': 'month',
                                    'order_id': 'orders',
                                    'weekday': 'weekday'}},
             'monthly': {'df': dforder_hourxm,
                         'x': "hour",
                         "y": "order_id",
                         "color": "month",
                         "title": "Evolution of Hour Monthly-Orders by hours",
                         "labels": {'month': 'month',
                                    'order_id': 'orders',
                                    'hour': 'hour'}},
             'hours': {'df': dforder_hourxm,
                       'x': "month",
                       "y": "order_id",
                       "color": "hour",
                       "title": "Evolution of each hour by month",
                       "labels": {'month': 'month',
                                  'order_id': 'order',
                                  'hour': 'hour'}},
             }

    fig = px.line(plots[chart_type]['df'],
                  x=plots[chart_type]['x'],
                  y=plots[chart_type]['y'],
                  color=plots[chart_type]['color'],
                  title=plots[chart_type]['title'],
                  labels=plots[chart_type]['labels'],
                  height=400,
                  )
    fig.update_traces(hoverinfo='text+name', mode='lines+markers')
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.2, ))

    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                       'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey',
                     zeroline=True, zerolinewidth=2, zerolinecolor='LightGrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey',
                     zeroline=True, zerolinewidth=2, zerolinecolor='LightGrey')

    return fig
