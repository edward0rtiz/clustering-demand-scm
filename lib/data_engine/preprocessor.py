import io
import os
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots

# from .s3_download_all import df_kiwer, df_order
from sklearn import preprocessing
from kmodes.kmodes import KModes
from sklearn.cluster import KMeans
from kneed import KneeLocator

import reverse_geocode

###########################################################
#
#           Preprocessing & data transformation
#
###########################################################


# Call databased from data dir
kiwers = "data/kiwersDB.csv"
orders = "data/ordersDB.csv"
berkeley_csv = "data/berkeley_cleaned.csv"
df_kiwer = pd.read_csv(kiwers)
df_order = pd.read_csv(orders)
ber = pd.read_csv(berkeley_csv)

# Drop Unnamed: 0 for df_order
df_order = df_order.drop(["Unnamed: 0"], axis=1)

# create a copy of the data extracted from S3
dfkiwer = df_kiwer.copy()
dforder = df_order.copy()
berkeley = ber.copy()

# Deleting unnecesary cols
dfkiwer = dfkiwer.drop(["epoch_timestamp"], axis=1)
dforder = dforder.drop(["readable_datetime"], axis=1)

# Transforming string to datetime
dfkiwer["readable_datetime"] = pd.to_datetime(
    dfkiwer["readable_datetime"], format="%Y-%m-%d %H:%M:%S"
)

# Transforming from timestamp to datetime
dforder[
    [
        "created",
        "assigned",
        "courier_arrived",
        "picked_up",
        "bot_loaded",
        "bot_dropped_off",
        "waiting_for_client",
        "closed",
    ]
] = dforder[
    [
        "created",
        "assigned",
        "courier_arrived",
        "picked_up",
        "bot_loaded",
        "bot_dropped_off",
        "waiting_for_client",
        "closed",
    ]
].apply(
    pd.to_datetime, unit="ms", origin="unix"
)

# Converting to categorical
dforder["type_of_delivery"] = dforder.type_of_delivery.astype("category")
dforder["payment_method"] = dforder.payment_method.astype("category")

# fill nan values
dforder["order_tip"].fillna(0, inplace=True)
values_1 = {"kiwer": "AndresCamiloAriza"}

dforder["bot_name"] = dforder["bot_name"].fillna(dforder["kiwer"])
dforder.loc[
    (dforder["bot_name"] == "kiwibot204") & (dforder["kiwer"].isnull())
    ] = dforder.loc[
    (dforder["bot_name"] == "kiwibot204") & (dforder["kiwer"].isnull())
    ].fillna(
    value=values_1
)
dforder = dforder.dropna(subset=["kiwer"])

# fill 0 values for nan
dforder[["client_lat", "client_lng"]] = dforder[["client_lat", "client_lng"]].replace(
    0, np.NaN
)

# replace value at restaunrat name fix typo of abbes pizza
dforder["restaurant_name"] = dforder["restaurant_name"].replace(
    "Abes pizza", "Abe's Pizza"
)

# fill nan in client_lat and client_lng
dforder = dforder.sort_values(by="client_readable_address")
dforder[["client_lat", "client_lng"]] = dforder[["client_lat", "client_lng"]].ffill()
dforder = dforder.sort_values(by=["client_lat", "client_lng"])
dforder["client_readable_address"] = dforder["client_readable_address"].ffill()

# Create total price
dforder["total_cost"] = (
        dforder["price_with_discounts"] + dforder["delivey_fee"] + dforder["order_tax"]
)

# create weekday, month and hour
dforder["hour"] = dforder["created"].dt.hour
dforder["month"] = dforder["created"].dt.month
dforder["weekday"] = dforder["created"].dt.day_name()
dforder["week_no"] = dforder["created"].dt.strftime("%U")

# create column diff_closed
dforder["diff_closed"] = dforder["closed"] - dforder["waiting_for_client"]
dforder["diff_closed"] = dforder["diff_closed"].dt.total_seconds() / 60

# Setting up conditions to see if order was approved, error or canceled
conditions = [
    (
        (
                (dforder["client_lat"] == dforder["restaurant_lat"])
                & (dforder["client_lng"] == dforder["restaurant_lng"])
                & (dforder["accepted_by_restaurant"].isna())
        )
    ),
    (
        (
                (dforder["client_lat"] != dforder["restaurant_lat"])
                & (dforder["client_lng"] != dforder["restaurant_lng"])
                & (dforder["accepted_by_restaurant"].isna())
        )
    ),
    ((dforder["load_battery"] == 100) & (dforder["wait_battery"] == 100)),
    (
            ((dforder["load_battery"] == 100) & (dforder["wait_battery"] == 100))
            & (dforder["accepted_by_restaurant"] is None)
    ),
]
values = ["canceled", "accepted", "error", "canceled"]
dforder["order_status"] = np.select(conditions, values)

# replace value 0 by approved
dforder["order_status"].replace({"0": "accepted"}, inplace=True)

# Converting the status to categorical
dforder["order_status"] = dforder.order_status.astype("category")

# From coordinates get the city
dforder['restaurant_city'] = reverse_geocode.search(dforder[['restaurant_lat', 'restaurant_lng']].values.tolist())
dforder['restaurant_city'] = dforder.apply(lambda x: x['restaurant_city']['city'], axis=1)

dforder['client_city'] = reverse_geocode.search(dforder[['client_lat', 'client_lng']].values.tolist())
dforder['client_city'] = dforder.apply(lambda x: x['client_city']['city'], axis=1)

# Convert readable datetime to datetime
dfkiwer["readable_datetime"] = pd.to_datetime(dfkiwer["readable_datetime"])

###########################################################
#
#          Dfkiwers preprocessing dataframes for plots
#
###########################################################

# Extract relevant information from date and time to perform EDA
dfkiwer["weekday"] = dfkiwer["readable_datetime"].dt.day_name()
dfkiwer["week"] = dfkiwer["readable_datetime"].dt.isocalendar().week
dfkiwer["month"] = dfkiwer["readable_datetime"].dt.month

############ [Data Plot 1/9] Historial logs by dates ###############
dfkiwer_dates = (
    dfkiwer["readable_datetime"]
        .dt.date.rename_axis("Date")
        .reset_index()
        .sort_values("readable_datetime")
        .value_counts("readable_datetime", sort=False)
        .rename_axis("Date")
        .reset_index(name="Logs")
)

################ [Data Plot 2/9] Logs by day ###################
# Converting weekdays to categoricals, and setting days orders.
dfkiwer["weekday"] = pd.Categorical(
    dfkiwer["weekday"],
    categories=[
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ],
    ordered=True,
)

dfkiwer_days = (
    dfkiwer["weekday"]
        .value_counts(sort=False)
        .rename_axis("Weekday")
        .reset_index(name="Logs")
)

############ [Data Plot 3/9] Evolution of Weekdays ###############
# Create a dataframe with the groupby of weekday and month
multiple_weekday = dfkiwer.groupby(by=["weekday", "month"], as_index=False)[
    "username"
].count()

################ [Data Plot 4/9 Total logs by hour ################
# Create a dataframe with the kiwers total count per hours
dfkiwer_hours = (
    dfkiwer["readable_datetime"]
        .dt.hour.value_counts(sort=False)
        .rename_axis("Hour")
        .reset_index(name="Logs")
)

######## [Data Plot 5/9] Evolution of each hour by month ###############
# Create a dataframe of kiwers hours per month
dfkiwer["hour"] = dfkiwer["readable_datetime"].dt.hour
kiwers_hxm = dfkiwer.groupby(by=["hour", "month"], as_index=False)["username"].count()

################ [Data Plot 6/9] Logs by month ###############
# Create a dataframe of kiwers month value counts
dfkiwer_month = (
    dfkiwer.value_counts("month", sort=False)
        .rename_axis("Month")
        .reset_index(name="Logs")
)

################ [Data Plot 7/9] Logs by week ###############
dfkiwer_weeks = (
    dfkiwer.value_counts("week", sort=False)
        .rename_axis("Week")
        .reset_index(name="Logs")
)

################ [Data Plot 8/9] Evolution of day by weeks #############
kiwers_dayxw = dfkiwer.groupby(by=["weekday", "week"], as_index=False)[
    "username"
].count()

###################[Data Plot 9/9] Logs Location ######################
# MAP
kiwer_map = px.scatter_mapbox(
    df_kiwer,
    lat="lat",
    lon="lng",
    color_discrete_sequence=["fuchsia"],
    zoom=1,
    height=500,
)
kiwer_map.update_layout(mapbox_style="open-street-map")
kiwer_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

# ###########################################################
# #
# #          Dforders preprocessing dataframes for plots
# #
# ###########################################################

##################### [Plot 1/17: Parallel Plot] Parallel plot by orders ############################

dforder_bot = dforder.copy()
drop_cols = [
    "client_id",
    "client_lat",
    "client_lng",
    "client_readable_address",
    "restaurant_id",
    "restaurant_name",
    "restaurant_readable_address",
    "restaurant_lat",
    "restaurant_lng",
    "price_with_discounts",
    "delivey_fee",
    "order_tax",
    "created",
    "assigned",
    "accepted_by_restaurant",
    "courier_arrived",
    "picked_up",
    "bot_loaded",
    "bot_dropped_off",
    "waiting_for_client",
    "closed",
    "delivery_time",
    "load_lat",
    "load_lng",
    "load_battery",
    "wait_lat",
    "wait_lng",
    "wait_battery",
    "total_cost",
    "diff_closed",
    "order_tip",
]

dforder_bot = dforder_bot.drop(drop_cols, axis=1)

# Build parcats dimensions
categorical_dimensions = [
    "type_of_delivery",
    "client_is_prime",
    "payment_method",
    "order_status",
]

dimensions = [
    dict(values=dforder_bot[label], label=label) for label in categorical_dimensions
]

# Build colorscale
color = np.zeros(len(dforder_bot), dtype="uint8")
colorscale = [[0, "gray"], [1, "firebrick"]]

# Build figure as FigureWidget
parallel = go.FigureWidget(
    data=[
        go.Scatter(
            x=dforder_bot.bot_name,
            y=dforder_bot["price_without_discounts"],
            marker={"color": "gray"},
            mode="markers",
            selected={"marker": {"color": "firebrick"}},
            unselected={"marker": {"opacity": 0.3}},
        ),
        go.Parcats(
            domain={"y": [0, 0.4]},
            dimensions=dimensions,
            line={
                "colorscale": colorscale,
                "cmin": 0,
                "cmax": 1,
                "color": color,
                "shape": "hspline",
            },
        ),
    ]
)

parallel.update_layout(
    height=800,
    xaxis={"title": "bot_name"},
    yaxis={"title": "total_orders", "domain": [0.6, 1]},
    dragmode="lasso",
    hovermode="closest",
)


# Update color callback
def update_color(trace, points, state):
    # Update scatter selection
    parallel.data[0].selectedpoints = points.point_inds

    # Update parcats colors
    new_color = np.zeros(len(dforder_bot), dtype="uint8")
    new_color[points.point_inds] = 1
    parallel.data[1].line.color = new_color


# Register callback on scatter selection...
parallel.data[0].on_selection(update_color)
# and parcats click
parallel.data[1].on_click(update_color)

parallel.update_layout(
    {
        "plot_bgcolor": "rgba(0, 0, 0, 0)",
        "paper_bgcolor": "rgba(0, 0, 0, 0)",
    }
)
parallel.update_xaxes(
    showgrid=True,
    gridwidth=1,
    gridcolor="LightGrey",
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor="LightGrey",
)
parallel.update_yaxes(
    showgrid=True,
    gridwidth=1,
    gridcolor="LightGrey",
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor="LightGrey",
)

################## [Plot 2/17 Heatmap] Correlation of cols ######################
dfcorr = dforder[
    [
        "price_without_discounts",
        "price_with_discounts",
        "delivey_fee",
        "order_tax",
        "order_tip",
        "total_cost",
    ]
].corr()
dfcorr_list = []
for i in list(dfcorr):
    dfcorr_list.append(dfcorr[i].round(2).tolist())
x_list = [
    "price_without_discounts",
    "price_with_discounts",
    "delivey_fee",
    "order_tax",
    "order_tip",
    "total_cost",
]
y_list = [
    "price_without_discounts",
    "price_with_discounts",
    "delivey_fee",
    "order_tax",
    "order_tip",
    "total_cost",
]
heatmap_1 = ff.create_annotated_heatmap(
    z=dfcorr_list, x=x_list, y=y_list, annotation_text=dfcorr_list, colorscale="Viridis"
)
heatmap_1.layout.width = 600

################# [Plot 3/17 Heatmap] Correlation of cols ########################
dfcorr2 = dforder[
    [
        "client_is_prime",
        "price_without_discounts",
        "price_with_discounts",
        "delivey_fee",
        "order_tax",
        "order_tip",
        "delivery_time",
        "load_battery",
        "wait_battery",
        "total_cost",
        "diff_closed",
        "hour",
        "month",
    ]
].corr()

dfcorr_list2 = []
for i in list(dfcorr2):
    dfcorr_list2.append(dfcorr2[i].round(2).tolist())

x_list2 = [
    "client_is_prime",
    "price_without_discounts",
    "price_with_discounts",
    "delivey_fee",
    "order_tax",
    "order_tip",
    "delivery_time",
    "load_battery",
    "wait_battery",
    "total_cost",
    "diff_closed",
    "hour",
    "month",
]
y_list2 = [
    "client_is_prime",
    "price_without_discounts",
    "price_with_discounts",
    "delivey_fee",
    "order_tax",
    "order_tip",
    "delivery_time",
    "load_battery",
    "wait_battery",
    "total_cost",
    "diff_closed",
    "hour",
    "month",
]
heatmap_2 = ff.create_annotated_heatmap(
    z=dfcorr_list2,
    x=x_list2,
    y=y_list2,
    annotation_text=dfcorr_list2,
    colorscale="Viridis",
)
for i in range(len(heatmap_2.layout.annotations)):
    heatmap_2.layout.annotations[i].font.size = 8
heatmap_2.layout.width = 600

######################### [Plot 4/17 Data Type of client #########################
dfcust = dforder[["created", "client_id", "client_is_prime", "week_no"]].sort_values(
    by=["client_id", "created"]
)
cust_dict = {"Prime": 0, "Not Prime": 0, "Swing": 0}
for cust in dfcust["client_id"].unique():
    states = dfcust[dfcust["client_id"] == cust]["client_is_prime"]

    if all(states):
        cust_dict["Prime"] += 1
    elif not any(states):
        cust_dict["Not Prime"] += 1
    else:
        cust_dict["Swing"] += 1

df_type_client = (
    pd.Series(cust_dict)
        .reset_index()
        .rename(columns={"index": "Type of Client", 0: "Number of Clients"})
)
df_type_client = df_type_client.assign(Client=["Client", "Client", "Client"])

type_plot = px.bar(
    df_type_client,
    x="Client",
    y="Number of Clients",
    color="Type of Client",
    title="Type of Client",
    height=400,
)
type_plot.update_layout(
    {
        "plot_bgcolor": "rgba(0, 0, 0, 0)",
        "paper_bgcolor": "rgba(0, 0, 0, 0)",
    }
)
type_plot.update_xaxes(
    showgrid=True,
    gridwidth=1,
    gridcolor="LightGrey",
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor="LightGrey",
)
type_plot.update_yaxes(
    showgrid=True,
    gridwidth=1,
    gridcolor="LightGrey",
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor="LightGrey",
)

# ############ [Plot 5/17] Type of client by week ###############
dfcusttable = dforder.sort_values(by=["week_no", "client_id"])
dfcusttable["Prime"] = dfcusttable["client_is_prime"].replace([False, True], [0, 1])
dfcusttable["No Prime"] = dfcusttable["client_is_prime"].replace([False, True], [1, 0])
dfcusttable = dfcusttable.groupby(["week_no"]).agg(
    {"Prime": ["sum"], "No Prime": ["sum"]}
)
dfcusttable.reset_index(inplace=True)
dfcusttable.columns = dfcusttable.columns.droplevel(1)
client_count_plot = go.Figure(
    data=[
        go.Bar(name="Prime", x=dfcusttable["week_no"], y=dfcusttable["Prime"]),
        go.Bar(name="No Prime", x=dfcusttable["week_no"], y=dfcusttable["No Prime"]),
    ]
)
client_count_plot.update_layout(
    barmode="stack", title_text="Count type of client by week"
)
client_count_plot.update_layout(
    {
        "plot_bgcolor": "rgba(0, 0, 0, 0)",
        "paper_bgcolor": "rgba(0, 0, 0, 0)",
    }
)
client_count_plot.update_xaxes(
    showgrid=True,
    gridwidth=1,
    gridcolor="LightGrey",
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor="LightGrey",
)
client_count_plot.update_yaxes(
    showgrid=True,
    gridwidth=1,
    gridcolor="LightGrey",
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor="LightGrey",
)

############################# [6/17 Plot] Orders by date range ###################################
dforder_dates = dforder.copy()
dforder_dates["creation_date"] = dforder["created"].dt.date
dforder_dates = (
    dforder_dates.groupby("creation_date", sort=True)
        .sum()
        .rename(columns={"client_is_prime": "orders"})
)
dforder_dates.index = pd.to_datetime(dforder_dates.index)

############################# [7/17 Plot] Orders by week ###################################
dforder_weeks = (
    dforder.groupby("week_no").sum().rename(columns={"client_is_prime": "orders"})
)

############################# [8/17 Plot] Orders by Day ####################################
dforder["weekday"] = pd.Categorical(
    dforder["weekday"],
    categories=[
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ],
    ordered=True,
)

dforder_days = (
    dforder["weekday"]
        .value_counts(sort=False)
        .rename_axis("Weekday")
        .reset_index(name="Orders")
)

############################## [9/17 Plot] Orders by Hour ######################################
dforder_hours = dforder["created"].dt.hour.value_counts(sort=False).rename_axis("Hour")
dforder_hours = dforder_hours.reset_index(name="Orders").sort_values("Hour")

###################### [10/17 Plot] Evolution of Weekday-Orders by month ###################
dforder_xm = dforder.groupby(by=["weekday", "month"], as_index=False)[
    "order_id"
].count()

############# [11/17 Plot] Evolution of Hour Monthly-Orders by hours ################
############## [12/17 Plot] Evolution of each hour by month ###############
dforder_hourxm = dforder.groupby(by=["hour", "month"], as_index=False)[
    "order_id"
].count()

########################[13/17 Plot] Boxplots: take data from dforder ######################
boxplot_cost = make_subplots(
    rows=1, cols=2, subplot_titles=("By payment method", "By Client is prime")
)
boxplot_cost.add_trace(
    go.Box(x=dforder["payment_method"], y=dforder["total_cost"]), row=1, col=1
)
boxplot_cost.add_trace(
    go.Box(x=dforder["client_is_prime"], y=dforder["total_cost"]), row=1, col=2
)
boxplot_cost.update_layout(
    title_text="Total Cost (USD) by Payment method and Type of client"
)
boxplot_cost.update_layout(
    {"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"}
)
boxplot_cost.update_xaxes(
    showgrid=True,
    gridwidth=1,
    gridcolor="LightGrey",
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor="LightGrey",
)
boxplot_cost.update_yaxes(
    showgrid=True,
    gridwidth=1,
    gridcolor="LightGrey",
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor="LightGrey",
)

################################[14/17 Plot] Total cost ###################################
dforder_totalcostxw = dforder.groupby("week_no").sum().reset_index()
totalcost_byweek = px.bar(
    dforder_totalcostxw, x="week_no", y="total_cost", title="Total cost by weeks"
)
totalcost_byweek.update_layout(
    {"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"}
)
totalcost_byweek.update_xaxes(
    showgrid=True,
    gridwidth=1,
    gridcolor="LightGrey",
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor="LightGrey",
)
totalcost_byweek.update_yaxes(
    showgrid=True,
    gridwidth=1,
    gridcolor="LightGrey",
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor="LightGrey",
)

############################### [15/17 Plot] Total tips by hour ##############################
dforder_tipsxh = dforder[dforder["order_tip"] > 0].groupby("hour").sum().reset_index()
tips_hour = px.bar(
    dforder_tipsxh,
    x="hour",
    y="order_tip",
    title="Total tips by hour",
    labels={"hour": "Hour", "order_tip": "Tips (USD)"},
)
tips_hour.update_layout(
    {"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"}
)
tips_hour.update_xaxes(
    showgrid=True,
    gridwidth=1,
    gridcolor="LightGrey",
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor="LightGrey",
)
tips_hour.update_yaxes(
    showgrid=True,
    gridwidth=1,
    gridcolor="LightGrey",
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor="LightGrey",
)

###################### [16/17 Plot] Bots demand by hour on busiest day #######################
busiest_day = dforder["created"].dt.date.value_counts().reset_index()
busiest_day = busiest_day.iloc[0]["index"]
dforder_busiest_day = dforder[
    (dforder["type_of_delivery"] == "bot") & (dforder["created"].dt.date == busiest_day)
    ]
dforder_busiest_day = (
    dforder_busiest_day.groupby(["hour"])["bot_name"].unique().str.len().reset_index()
)
bots_busiest_day = px.bar(
    dforder_busiest_day,
    x="hour",
    y="bot_name",
    title="Bots demand by hour on busiest day",
    labels={"hour": "Hour", "bot_name": "Number of bots"},
)
bots_busiest_day.update_layout(
    {"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"}
)
bots_busiest_day.update_xaxes(
    showgrid=True,
    gridwidth=1,
    gridcolor="LightGrey",
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor="LightGrey",
)
bots_busiest_day.update_yaxes(
    showgrid=True,
    gridwidth=1,
    gridcolor="LightGrey",
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor="LightGrey",
)

############################  [17/17 Plot] Number of orders made by prime client - Price ##################
dforder_res = dforder.groupby("restaurant_name").sum().reset_index()
restaurant_summary = px.scatter(
    dforder_res,
    x="client_is_prime",
    y="restaurant_name",
    size="price_with_discounts",
    hover_data=["client_is_prime", "price_with_discounts"],
    height=1200,
    title="Number of orders made by prime client - Price",
)
restaurant_summary.update_layout(
    {"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"}
)
restaurant_summary.update_xaxes(
    showgrid=True,
    gridwidth=1,
    gridcolor="LightGrey",
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor="LightGrey",
)
restaurant_summary.update_yaxes(
    showgrid=True,
    gridwidth=1,
    gridcolor="LightGrey",
    zeroline=True,
    zerolinewidth=2,
    zerolinecolor="LightGrey",
)

# ************************* OPTIONAL PLOTS FOR ORDERS ANALYTICS ****************************
# ################### Evolution of restaurants orders by month #################
# dforder_res_mo = pd.pivot_table(dforder, index=['restaurant_name', 'month'], values=["client_is_prime"],
#                                 aggfunc=np.sum).fillna(0).reset_index().sort_values('restaurant_name')
# dforder_res_mo.rename(columns={'client_is_prime': 'orders'})

# ################### Evolution of restaurants orders by week #################
# dforder_res_week = pd.pivot_table(dforder, index=['restaurant_name', 'week_no'], values=["client_is_prime"],
#                                   aggfunc=np.sum).fillna(0).reset_index().sort_values('restaurant_name')
# dforder_res_week.rename(columns={'client_is_prime': 'orders'})


# ################### Number of orders made by prime client - Price #################
# ################### Number of orders made by prime client - Tips #################
# dforder_res = dforder.groupby('restaurant_name').sum().reset_index()

# ### ¡¡¡OJO!!! df_week arriba - Evolution of restaurant prime clients by week ######


# ################### Type of client restaurant, divided by week #################
# dforder_accepted_mo = dforder[[
#     'restaurant_name', 'week_no', 'accepted_by_restaurant', 'client_is_prime']]
# dforder_accepted_mo['accepted_by_restaurant'] = dforder_accepted_mo['accepted_by_restaurant'].fillna(
#     pd.Timedelta(seconds=0))
# dforder_accepted_mo['accepted_by_restaurant'] = dforder_accepted_mo['accepted_by_restaurant'].astype(
#     str)
# dforder_accepted_mo['accepted_by_restaurant'] = dforder_accepted_mo['accepted_by_restaurant'].replace(
#     to_replace=r'[^0 days 00:00:00	]', value='1', regex=True)
# dforder_accepted_mo['accepted_by_restaurant'] = dforder_accepted_mo['accepted_by_restaurant'].replace(
#     to_replace=r'[0 days 00:00:00	]', value='0', regex=True)
# dforder_accepted_mo['accepted_by_restaurant'] = dforder_accepted_mo['accepted_by_restaurant'].str[:1]
# dforder_accepted_mo = pd.pivot_table(dforder_accepted_mo, index=['restaurant_name', 'week_no', 'accepted_by_restaurant'],
#                                      values=["client_is_prime"],
#                                      aggfunc=np.sum).fillna(0).reset_index().sort_values(by=['restaurant_name', 'week_no'],
#                                                                                          ascending=[True, True])


# ###########################################################
# #
# #          Preprocessing data for clusterization
# #
# ###########################################################

# Create a copy from dforder
dforder['restaurant_city'] = reverse_geocode.search(dforder[['restaurant_lat', 'restaurant_lng']].values.tolist())
dforder['restaurant_city'] = dforder.apply(lambda x: x['restaurant_city']['city'], axis=1)
dforder['restaurant_city'].unique()

dforder['client_city'] = reverse_geocode.search(dforder[['client_lat', 'client_lng']].values.tolist())
dforder['client_city'] = dforder.apply(lambda x: x['client_city']['city'], axis=1)
dforder['client_city'].unique()

dfreg = dforder.copy()

dfreg['hour'] = dfreg['hour'].astype('category')
dfreg['week_no'] = dfreg['week_no'].astype('category')
dfreg['month'] = dfreg['month'].astype('category')

dfreg['accepted_by_restaurant'] = dfreg['accepted_by_restaurant'].fillna(
    pd.Timedelta(seconds=0))
dfreg['accepted_by_restaurant'] = dfreg['accepted_by_restaurant'].astype(str)
dfreg['accepted_by_restaurant'] = dfreg['accepted_by_restaurant'].replace(
    to_replace=r'[^0 days 00:00:00	]', value='1', regex=True)
dfreg['accepted_by_restaurant'] = dfreg['accepted_by_restaurant'].replace(
    to_replace=r'[0 days 00:00:00	]', value='0', regex=True)
dfreg['accepted_by_restaurant'] = dfreg['accepted_by_restaurant'].str[:1]

# create price category
dfreg.loc[((dfreg['total_cost'] > -15) &
           (dfreg['total_cost'] <= 0)), 'price_cat'] = 1
dfreg.loc[((dfreg['total_cost'] > 0) & (
        dfreg['total_cost'] <= 5)), 'price_cat'] = 2
dfreg.loc[((dfreg['total_cost'] > 5) & (
        dfreg['total_cost'] <= 10)), 'price_cat'] = 3
dfreg.loc[((dfreg['total_cost'] > 10) & (
        dfreg['total_cost'] <= 15)), 'price_cat'] = 4
dfreg.loc[((dfreg['total_cost'] > 15) & (
        dfreg['total_cost'] <= 20)), 'price_cat'] = 5
dfreg.loc[(dfreg['total_cost'] > 20), 'price_cat'] = 6

# crete price_cat_log
dfreg['price_cat'] = dfreg['price_cat'].astype('category')
dfreg.loc[((dfreg['price_cat'] == 1) | (dfreg['price_cat'] == 2)
           | (dfreg['price_cat'] == 3)), 'price_cat_log'] = 0
dfreg.loc[((dfreg['price_cat'] == 4) | (dfreg['price_cat'] == 5)
           | (dfreg['price_cat'] == 6)), 'price_cat_log'] = 1

# convert columns to categorical
dfreg['price_cat'] = dfreg['price_cat'].astype('category')
dfreg['client_is_prime'] = dfreg['client_is_prime'].astype('category')
dfreg['month'] = dfreg['month'].astype('category')
dfreg['weekday'] = dfreg['weekday'].astype('category')
dfreg['price_cat_log'] = dfreg['price_cat_log'].astype('category')
dfreg['accepted_by_restaurant'] = dfreg['accepted_by_restaurant'].astype(
    'category')

# create category codes
dfreg['client_cat'] = dfreg.client_is_prime.cat.codes
dfreg['price_cat'] = dfreg.price_cat.cat.codes
dfreg['cat_delivery'] = dfreg.type_of_delivery.cat.codes
dfreg['cat_payment'] = dfreg.payment_method.cat.codes
dfreg['cat_status'] = dfreg.order_status.cat.codes
dfreg['cat_weekday'] = dfreg.weekday.cat.codes
dfreg['cat_month'] = dfreg.month.cat.codes
dfreg['price_cat_log'] = dfreg.price_cat_log.cat.codes
dfreg['accepted_by_restaurant'] = dfreg.accepted_by_restaurant.cat.codes

# Add intercept
dfreg['Intercept'] = 1

# ###########################################################
# #
# #          Clusterization dataframe plots
# #
# ###########################################################

# Create a mastery copy for clusters
dforder_cluster = dfreg.copy()

# dataframe for clusterization model1
cols = ['order_id', 'client_lat', 'client_lng', 'restaurant_lat',
        'restaurant_lng', 'price_with_discounts', 'delivey_fee', 'order_tip',
        'total_cost', 'hour', 'week_no', 'month', 'delivery_time', 'wait_lat',
        'wait_lng', 'client_city', 'restaurant_city']
dforder_cluster1 = dforder_cluster[cols]

# # dataframe for clusterization model2
# cols2 = ['order_id', 'type_of_delivery', 'client_cat', 'price_cat',
#          'cat_delivery', 'cat_payment', 'accepted_by_restaurant', 'cat_status',
#          'cat_weekday', 'cat_month']
# dforder_cluster2 = dforder_cluster[cols2]q

# Clean for waiting time
dforder_cluster1 = dforder_cluster1.dropna()

dforder_cluster1['wait_city'] = reverse_geocode.search(dforder_cluster1[['wait_lat', 'wait_lng']].values.tolist())
dforder_cluster1['wait_city'] = dforder_cluster1.apply(lambda x: x['wait_city']['city'], axis=1)

# Define city
selected_city = 'Berkeley'
city = dforder_cluster1[(dforder_cluster1['client_city'] == selected_city) & \
                        (dforder_cluster1['restaurant_city'] == selected_city) & \
                        (dforder_cluster1['wait_city'] == selected_city) & \
                        (dforder_cluster1['total_cost'] > 0)]


def elbow_method(df=None):
    """Find the suggested number of clusters and plot the elbow diagram.

    args:
        df (pd.Dataframe): 2 columns dataframe

    returns:
        (k, fig) (int, go figure); (number of clusters, figure to plot)
    """

    sum_sq_d = []
    K = list(range(1, 11))

    for k in K:
        km = KMeans(n_clusters=k)
        km = km.fit(df)
        sum_sq_d.append(km.inertia_)

    kl = KneeLocator(range(1, 11), sum_sq_d, curve="convex", direction="decreasing")

    fig = go.Figure(data=go.Scatter(x=K, y=sum_sq_d))

    return kl.elbow


def simple_cluster(K=1, df=None):
    """Create and assign cluster to each point of datadrame.

    args:
      K (int): number of clusters.
      df (pd.Dataframe): 2 columns dataframe to clusterize.


    returns:
      px map figure
    """

    # Assign how many clusters (k-number) you would like to have
    K = K

    kmeans_model = KMeans(n_clusters=K, init='k-means++').fit(df)
    kmeans_model.inertia_

    # Iterative procedure to learn labels
    labels = kmeans_model.predict(df)

    df['cluster'] = pd.Series(labels, index=df.index)

    fig = px.scatter_mapbox(df,
                            lat=df.columns[0],
                            lon=df.columns[1],
                            color='cluster',
                            opacity=0.6,
                            zoom=13,
                            )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig


##################################################################
#########             Analysis for city              #############
##################################################################
map_neighborhood = px.scatter_mapbox(berkeley[berkeley['neighborhood'].notna()],
                                     lat="lat",
                                     lon="lng",
                                     hover_name="city",
                                     hover_data=["name"],
                                     color='neighborhood',
                                     zoom=11,
                                     title="Berkeley Neighborhoods"
                                     )
map_neighborhood.update_layout(mapbox_style="open-street-map")
map_neighborhood.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

berkeley['category'] = berkeley['category'].astype('category')
berkeley['postal_code'] = berkeley['postal_code'].astype('category')
berkeley['neighborhood'] = berkeley['neighborhood'].astype('category')

berkeley2 = pd.get_dummies(berkeley[['category']], prefix='', prefix_sep='')
berkeley2['neighborhood'] = berkeley['neighborhood']
berkeley2.drop(['neighborhood'], axis=1, inplace=True)
berkeley2.insert(loc=0, column='neighborhood', value=berkeley['neighborhood'])

berkeley3 = berkeley2.groupby('neighborhood').mean().reset_index()


def most_common_venues(row, top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)

    return row_categories_sorted.index.values[0:top_venues]


top10 = 10
columns = ['neighborhood']
indicator = ['ST', 'MD', 'RD']

for ind in np.arange(top10):
    try:
        columns.append('{}{} Most Common Venue'.format(ind + 1, indicator[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind + 1))

berkeley_merge = pd.DataFrame(columns=columns)
berkeley_merge['neighborhood'] = berkeley3['neighborhood']

for ind in np.arange(berkeley3.shape[0]):
    berkeley_merge.iloc[ind, 1:] = most_common_venues(berkeley3.iloc[ind, :], top10)

clusters = 4

berkeley_cluster = berkeley3.drop('neighborhood', axis=1)
berkeley_kmeans = KMeans(n_clusters=clusters).fit(berkeley_cluster)
# berkeley_kmeans.inertia_

# Iterative procedure to learn labels
labels = berkeley_kmeans.predict(berkeley_cluster)
# labels[:11]
# berkeley_cluster['labels'] = labels

# berkeley_cluster
berkeley_kmeans.labels_[:10]

berkeley_merge.insert(0, 'labels', berkeley_kmeans.labels_)

final_berkeley = berkeley.copy()
final_berkeley = final_berkeley.join(berkeley_merge.set_index('neighborhood'), on='neighborhood')
final_berkeley = final_berkeley.drop(columns=['id', 'state', "Unnamed: 0"], axis=1)

# clusters
map_city_clusters = px.scatter_mapbox(final_berkeley,
                                      lat="lat",
                                      lon="lng",
                                      hover_name="category",
                                      hover_data=["name"],
                                      color='labels',
                                      zoom=11,
                                      title='Clustering')
map_city_clusters.update_layout(mapbox_style="open-street-map")
map_city_clusters.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})