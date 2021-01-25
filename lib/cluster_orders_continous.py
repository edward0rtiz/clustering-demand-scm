import dash
from dash.dependencies import Input, Output

import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html

import plotly.express as px

import pandas as pd

from lib.data_engine.preprocessor import (dforder_cluster1,
                                          elbow_method,
                                          simple_cluster)

app = __import__("app").app

########################### Components ###############################################

cities = dforder_cluster1['restaurant_city'].unique()
city_list = [{'label': city, 'value': city} for city in cities]
city_selector = dcc.Dropdown(
    id='city-dropdown',
    options=city_list,
    value=city_list[0]['value'],
),

cluster_selector = dbc.FormGroup(
    [
        dbc.RadioItems(
            options=[
                {"label": "Restaurant", "value": "restaurant"},
                {"label": "Client", "value": "client"},
                {"label": "Waiting position", "value": "wait"},
            ],
            value="restaurant",
            id="radioitems-inline-location",
            inline=True,
        ),
    ]
)

number_k_input = html.Div(
    [
        html.P("Type a number outside the range 2-10"),
        dbc.Input(id="k-input", type="number", min=2, max=10, step=1, value=2),
    ],
)

############################ Layout ################################################

cluster_orders_layout = [
    dbc.Row(
        [
            dbc.Col(
                [
                    html.P("Please, select the city:"),
                    html.Div(city_selector)
                ]
            ),
        ],
    ),
    dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Label("Please, choose one location"),
                    html.Div(cluster_selector)
                ]
            ),
        ],
    ),
    dbc.Row(dbc.Col(dcc.Graph(id="plot-preview"))),
    dbc.Row(dbc.Col(html.Div(id="recommended-clusters"))),
    dbc.Row(dbc.Col(html.Div(number_k_input))),
    dbc.Row(dbc.Col(html.Div(dcc.Graph(id="plot-cluster")))),
    html.Div(id="df-cache", style={'display': 'none'})
]


# Dropdown to radios
@app.callback(
    Output("df-cache", "children"),
    Input("city-dropdown", "value"),
)
def subset_dataframe(selected_city):
    # Define city
    city = dforder_cluster1[(dforder_cluster1['client_city'] == selected_city) &
                            (dforder_cluster1['restaurant_city'] == selected_city) &
                            (dforder_cluster1['wait_city'] == selected_city) &
                            (dforder_cluster1['total_cost'] > 0)]

    return city.to_json()


# Plot the previous map
@app.callback(
    Output("plot-preview", "figure"),
    [Input("df-cache", "children"),
     Input("radioitems-inline-location", "value"),
     Input("city-dropdown", "value"),
     ]
)
def update_plot1(cached_df, cluster_type, selected_city):
    #  city_center = geocoder.osm(selected_city)
    city = pd.read_json(cached_df)

    if cluster_type == "restaurant":
        # map_restaurants = px.scatter_mapbox(city,
        #                                     lat="restaurant_lat",
        #                                     lon="restaurant_lng",
        #                                     center={"lat": city_center.lat, "lon": city_center.lng},
        #                                     color_discrete_sequence=["fuchsia"], zoom=13,)
        # map_restaurants.update_layout(mapbox_style="open-street-map")
        # map_restaurants.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        lat = "restaurant_lat"
        lng = "restaurant_lng"

    elif cluster_type == "client":
        lat = "client_lat"
        lng = "client_lng"

    elif cluster_type == "wait":
        lat = "wait_lat"
        lng = "wait_lng"

    map = px.scatter_mapbox(city,
                            lat=lat,
                            lon=lng,
                            #                       center={"lat": city_center.lat, "lon": city_center.lng},
                            color_discrete_sequence=["fuchsia"], zoom=13, )
    map.update_layout(mapbox_style="open-street-map")
    map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return map


# Suggest number of cluster
@app.callback(
    Output("recommended-clusters", "children"),
    [Input("df-cache", "children"),
     Input("radioitems-inline-location", "value"), ]
)
def suggest_cluster_number(cached_df, cluster_type):
    city = pd.read_json(cached_df)

    if cluster_type == 'restaurant':
        subset = ['restaurant_lng', 'restaurant_lat']
        n_clusters = elbow_method(city[subset])

    elif cluster_type == 'client':
        subset = ['client_lng', 'client_lat']
        n_clusters = elbow_method(city[subset])
    elif cluster_type == 'wait':
        subset = ['wait_lng', 'wait_lat']
        n_clusters = elbow_method(city[subset])

    return "The suggested number of clusters is: {}".format(n_clusters)


# Plot the clusters
@app.callback(
    Output("plot-cluster", "figure"),
    [Input("df-cache", "children"),
     Input("radioitems-inline-location", "value"),
     Input("k-input", "value")]
)
def plot_clusters(cached_df, cluster_type, n_clusters):
    city = pd.read_json(cached_df)

    if cluster_type == 'restaurant':
        subset = ['restaurant_lat', 'restaurant_lng']
    elif cluster_type == 'client':
        subset = ['client_lat', 'client_lng']
    elif cluster_type == 'wait':
        subset = ['wait_lat', 'wait_lng']

    fig = simple_cluster(K=n_clusters, df=city[subset])

    return fig
