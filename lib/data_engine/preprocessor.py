import pandas as pd
import numpy as np
import os
import io
from datetime import datetime
from s3_get_object_all import df_kiwer, df_order

# ploting
import plotly.express as px
import plotly.graph_objs as go

# clusteriztion modules
from sklearn import preprocessing
from kmodes.kmodes import KModes
from sklearn.cluster import KMeans
from kneed import KneeLocator

from sklearn.decomposition import PCA
from plotly import tools
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from termcolor import colored

###########################################################
#
#           Preprocessing & data transformation
#
###########################################################

# Drop Unnamed: 0 for df_order
df_order = df_order.drop(['Unnamed: 0'], axis=1)

# create a copy of the data extracted from S3
dfkiwer = df_kiwer.copy()
dforder = df_order.copy()

# Deleting unnecesary cols
dfkiwer = dfkiwer.drop(['epoch_timestamp'], axis=1)
dforder = dforder.drop(['readable_datetime'], axis=1)

# Transforming string to datetime
dfkiwer['readable_datetime'] = pd.to_datetime(
    dfkiwer['readable_datetime'], format='%Y-%m-%d %H:%M:%S')

# Transforming from timestamp to datetime
dforder[['created', 'assigned', 'courier_arrived', 'picked_up',
         'bot_loaded', 'bot_dropped_off', 'waiting_for_client',
         'closed']] = dforder[['created', 'assigned',
                               'courier_arrived', 'picked_up', 'bot_loaded',
                               'bot_dropped_off', 'waiting_for_client',
                               'closed']].apply(pd.to_datetime, unit='ms',
                                                origin='unix')

# Converting to categorical
dforder['type_of_delivery'] = dforder.type_of_delivery.astype('category')
dforder['payment_method'] = dforder.payment_method.astype('category')

# fill nan values
dforder['order_tip'].fillna(0, inplace=True)
values_1 = {'kiwer': 'AndresCamiloAriza'}

dforder['bot_name'] = dforder['bot_name'].fillna(dforder['kiwer'])
dforder.loc[(dforder['bot_name'] == 'kiwibot204') &
            (dforder['kiwer'].isnull())] = dforder.loc[(dforder['bot_name'] == 'kiwibot204') &
                                                       (dforder['kiwer'].isnull())].fillna(value=values_1)
dforder = dforder.dropna(subset=['kiwer'])

# fill 0 values for nan
dforder[['client_lat', 'client_lng']] = dforder[['client_lat',
                                                 'client_lng']].replace(0, np.NaN)

# replace value at restaunrat name fix typo of abbes pizza
dforder['restaurant_name'] = dforder['restaurant_name'].replace('Abes pizza',
                                                                "Abe's Pizza")

# fill nan in client_lat and client_lng
fill_col = ['client_lat', 'client_lng']
dforder = dforder.sort_values(by='client_readable_address')
dforder[fill_col] = dforder[fill_col].ffill()
dforder = dforder.sort_values(by=fill_col)
dforder['client_readable_address'] = dforder['client_readable_address'].ffill()

# Create total price
dforder['total_cost'] = dforder['price_with_discounts'] + \
                        dforder['delivey_fee'] + dforder['order_tax']

# create weekday, month and hour
dforder['hour'] = dforder['created'].dt.hour
dforder['month'] = dforder['created'].dt.month
dforder['weekday'] = dforder['created'].dt.day_name()
dforder['week_no'] = dforder['created'].dt.strftime('%U')

# create column diff_closed
dforder['diff_closed'] = dforder['closed'] - dforder['waiting_for_client']
dforder['diff_closed'] = dforder['diff_closed'].dt.total_seconds() / 60

# Setting up conditions to see if order was approved, error or canceled
conditions = [(((dforder['client_lat'] == dforder['restaurant_lat']) &
                (dforder['client_lng'] == dforder['restaurant_lng']) &
                (dforder['accepted_by_restaurant'].isna()))),
              (((dforder['client_lat'] != dforder['restaurant_lat']) &
                (dforder['client_lng'] != dforder['restaurant_lng']) &
                (dforder['accepted_by_restaurant'].isna()))),
              ((dforder['load_battery'] == 100) & (dforder['wait_battery'] == 100)),
              (((dforder['load_battery'] == 100) & (dforder['wait_battery'] == 100)) &
               (dforder['accepted_by_restaurant'] is None))]

values = ['canceled', 'accepted', 'error', 'canceled']
dforder['order_status'] = np.select(conditions, values)

# replace value 0 by approved
dforder["order_status"].replace({"0": "accepted"}, inplace=True)

# Converting the status to categorical
dforder['order_status'] = dforder.order_status.astype('category')

# Convert readable datetime to datetime
dfkiwer['readable_datetime'] = pd.to_datetime(dfkiwer['readable_datetime'])

###########################################################
#
#          Dfkiwers preprocessing dataframes for plots
#
###########################################################

# Extract relevant information from date and time to perform EDA
dfkiwer['weekday'] = dfkiwer['readable_datetime'].dt.day_name()
dfkiwer['week'] = dfkiwer['readable_datetime'].dt.week
dfkiwer['month'] = dfkiwer['readable_datetime'].dt.month

################ [Data Plot 1/7] Logs by day ###################
# Converting weekdays to categoricals, and setting days orders.
dfkiwer['weekday'] = pd.Categorical(dfkiwer['weekday'],
                                    categories=['Monday',
                                                                    'Tuesday',
                                                                    'Wednesday',
                                                                    'Thursday',
                                                                    'Friday',
                                                                    'Saturday',
                                                                    'Sunday'],
                                    ordered=True)

dfkiwer_days = dfkiwer['weekday'].value_counts(sort=False).rename_axis('Weekday').reset_index(name='Logs')

############ [Data Plot 2/7] Evolution of Weekdays ###############
# Create a dataframe with the groupby of weekday and month
multiple_weekday = dfkiwer.groupby(by=['weekday',
                                       'month'], as_index=False)['username'].count()

################ [Data Plot 3/7] Total logs by hour ################
# Create a dataframe with the kiwers total count per hours
dfkiwer_hours = dfkiwer['readable_datetime'].dt.hour.value_counts(
    sort=False).rename_axis('Hour').reset_index(name='Logs')

######## [Data Plot 4/7] Evolution of each hour by month ###############
# Create a dataframe of kiwers hours per month
dfkiwer['hour'] = dfkiwer['readable_datetime'].dt.hour
kiwers_hxm = dfkiwer.groupby(
    by=['hour', 'month'], as_index=False)['username'].count()

################ [Data Plot 5/7] Logs by month ###############
# Create a dataframe of kiwers month value counts
dfkiwer_month = dfkiwer.value_counts(
    'month', sort=False).rename_axis('Month').reset_index(name='Logs')

################ [Data Plot 6/7] Logs by week ###############
dfkiwer_weeks = dfkiwer.value_counts(
    'week', sort=False).rename_axis('Week').reset_index(name='Logs')

################ [Data Plot 7/7] Evolution of day by weeks ###############
kiwers_dxw = dfkiwer.groupby(by=['weekday', 'week'], as_index=False)[
    'username'].count()

###########################################################
#
#          Dforders preprocessing dataframes for plots
#
###########################################################

################ [Parallel Plot] Parallel plot by orders ###############

dforder_bot = dforder.copy()
to_drop = ['client_id', 'client_lat', 'client_lng', 'client_readable_address',
           'restaurant_id', 'restaurant_name', 'restaurant_readable_address',
           'restaurant_lat', 'restaurant_lng', 'price_with_discounts',
           'delivey_fee', 'order_tax', 'created', 'assigned',
           'accepted_by_restaurant', 'courier_arrived', 'picked_up', 'bot_loaded',
           'bot_dropped_off', 'waiting_for_client', 'closed', 'delivery_time',
           'load_lat', 'load_lng', 'load_battery', 'wait_lat', 'wait_lng',
           'wait_battery', 'total_cost', 'diff_closed', 'order_tip']

# Dropping unnecesary columns for  parallel diagram
dforder_bot = dforder_bot.drop(to_drop, axis=1)

################ [Heatmap Plot] Correlation of cols ###############
corr = ['price_without_discounts', 'price_with_discounts', 'delivey_fee',
        'order_tax', 'order_tip', 'total_cost']
dfcorr = dforder[corr].corr()
dfcorr_list = []

for i in list(dfcorr):
    dfcorr_list.append(dfcorr[i].round(2).tolist())

x_list = ['price_without_discounts', 'price_with_discounts',
          'delivey_fee', 'order_tax', 'order_tip', 'total_cost']
y_list = ['price_without_discounts', 'price_with_discounts',
          'delivey_fee', 'order_tax', 'order_tip', 'total_cost']

################ [Heatmap Plot] Correlation of cols ###############
corr2 = ['client_is_prime', 'price_without_discounts', 'price_with_discounts',
         'delivey_fee', 'order_tax', 'order_tip', 'delivery_time',
         'load_battery', 'wait_battery', 'total_cost', 'diff_closed', 'hour',
         'month']
dfcorr2 = dforder[corr2].corr()

dfcorr_list2 = []

for i in list(dfcorr2):
    dfcorr_list2.append(dfcorr2[i].round(2).tolist())

x_list2 = ['client_is_prime', 'price_without_discounts', 'price_with_discounts',
           'delivey_fee', 'order_tax', 'order_tip', 'delivery_time',
           'load_battery', 'wait_battery', 'total_cost', 'diff_closed', 'hour',
           'month']

y_list2 = ['client_is_prime', 'price_without_discounts', 'price_with_discounts',
           'delivey_fee', 'order_tax', 'order_tip', 'delivery_time',
           'load_battery', 'wait_battery', 'total_cost', 'diff_closed', 'hour',
           'month']

################ [Data Plot] Type of client ###############
dfcust = dforder[['created', 'client_id', 'client_is_prime',
                  'week_no']].sort_values(by=['client_id', 'created'])

cust_dict = {'Prime': 0, 'Not Prime': 0, 'Swing': 0}

for cust in dfcust['client_id'].unique():
    states = dfcust[dfcust['client_id'] == cust]['client_is_prime']

    if all(states):
        cust_dict['Prime'] += 1
    elif not any(states):
        cust_dict['Not Prime'] += 1
    else:
        cust_dict['Swing'] += 1

df_type_client = pd.Series(cust_dict).reset_index().rename(
    columns={'index': 'Type of Client', 0: 'Number of Clients'})
df_type_client = df_type_client.assign(Client=['Client', 'Client', 'Client'])

############ [XXXX Plot] Type of client by week ###############
dfcusttable = dforder.sort_values(by=['week_no', 'client_id'])
dfcusttable['Prime'] = dfcusttable['client_is_prime'].replace([False, True], [
    0, 1])
dfcusttable['No Prime'] = dfcusttable['client_is_prime'].replace([False, True], [
    1, 0])
dfcusttable = dfcusttable.groupby(['week_no']).agg(
    {'Prime': ['sum'], 'No Prime': ['sum']})
dfcusttable.reset_index(inplace=True)
dfcusttable.columns = dfcusttable.columns.droplevel(1)

############ [XXXX Plot] Historical orders ###############
dforder_dates = dforder['created'].dt.date.rename_axis('Date').reset_index().sort_values(
    'created').value_counts('created', sort=False).rename_axis('Date').reset_index(name='Orders')

############ [XXXX Plot] Total cost vs weeks ###############
dforder_week_no_count = dforder.groupby('week_no').sum().reset_index()

############ [XXXX Plot] Orders by Day ###############
dforder['weekday'] = pd.Categorical(dforder['weekday'],
                                    categories=['Monday',
                                                'Tuesday',
                                                'Wednesday',
                                                'Thursday',
                                                'Friday',
                                                'Saturday',
                                                'Sunday'],
                                    ordered=True)

dforder_days = dforder['weekday'].value_counts(
    sort=False).rename_axis('Weekday').reset_index(name='Orders')

############ [XXXX Plot] Evolution of dat orders by month ###############
orders_xm = dforder.groupby(by=['weekday', 'month'], as_index=False)[
    'order_id'].count()

############ [XXXX Plot] Total order by hour ###############
dforder_hours = dforder['created'].dt.hour.value_counts(
    sort=False).rename_axis('Hour').reset_index(name='Orders').sort_values('Hour')

############ [XXXX Plot] Rush Hours by month ###############
############ [XXXX Plot] Evolution of each hour by month ###############

rush_hours = dforder.groupby(by=['hour', 'month'], as_index=False)[
    'order_id'].count()

############ [XXXX Plot] Total bot number by hour ###############
dforder_robots_hour = dforder[dforder['type_of_delivery'] == 'bot'].groupby(
    'hour')['bot_name'].unique().str.len().rename_axis('hour').reset_index()

############ [XXXX Plot] Total bot number by hour on busiest day ###############
day = dforder[(dforder['created'] > datetime(2019, 5, 13, 23, 59, 59)) & (
        dforder['created'] < datetime(2019, 5, 15, 0, 0, 0))]
day_bots = day[day['type_of_delivery'] == 'bot'].groupby(
    'hour')['bot_name'].unique().str.len().rename_axis('hour').reset_index()

######################## Boxplots: take data from dforder ######################
################### Total tips by hour: take data from dforder #################


################### Evolution of restaurants orders by month #################
dforder_res_mo = pd.pivot_table(dforder,
                                index=['restaurant_name', 'month'],
                                values=["client_is_prime"],
                                aggfunc=np.sum).fillna(0).reset_index().sort_values('restaurant_name')

dforder_res_mo.rename(columns={'client_is_prime': 'orders'})

################### Evolution of restaurants orders by week #################
dforder_res_week = pd.pivot_table(dforder,
                                  index=['restaurant_name', 'week_no'],
                                  values=["client_is_prime"],
                                  aggfunc=np.sum).fillna(0).reset_index().sort_values('restaurant_name')
dforder_res_week.rename(columns={'client_is_prime': 'orders'})

################### Number of orders made by prime client - Price #################
################### Number of orders made by prime client - Tips #################
dforder_res = dforder.groupby('restaurant_name').sum().reset_index()

### ¡¡¡OJO!!! df_week arriba - Evolution of restaurant prime clients by week ######


################### Type of client restaurant, divided by week #################
dforder_accepted_mo = dforder[[
    'restaurant_name', 'week_no', 'accepted_by_restaurant', 'client_is_prime']]
dforder_accepted_mo['accepted_by_restaurant'] = dforder_accepted_mo['accepted_by_restaurant'].fillna(
    pd.Timedelta(seconds=0))
dforder_accepted_mo['accepted_by_restaurant'] = dforder_accepted_mo['accepted_by_restaurant'].astype(
    str)
dforder_accepted_mo['accepted_by_restaurant'] = dforder_accepted_mo['accepted_by_restaurant'].replace(
    to_replace=r'[^0 days 00:00:00	]', value='1', regex=True)
dforder_accepted_mo['accepted_by_restaurant'] = dforder_accepted_mo['accepted_by_restaurant'].replace(
    to_replace=r'[0 days 00:00:00	]', value='0', regex=True)
dforder_accepted_mo['accepted_by_restaurant'] = dforder_accepted_mo['accepted_by_restaurant'].str[:1]
dforder_accepted_mo = pd.pivot_table(dforder_accepted_mo,
                                     index=['restaurant_name', 'week_no', 'accepted_by_restaurant'],
                                     values=["client_is_prime"],
                                     aggfunc=np.sum).fillna(0).reset_index().sort_values(
    by=['restaurant_name', 'week_no'],
    ascending=[True, True])

###########################################################
#
#          Preprocessing data for clusterization
#
###########################################################

# Create a copy from dforder
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

###########################################################
#
#          Clusterization dataframe plots
#
###########################################################

# Create a mastery copy for clusters
dforder_cluster = dfreg.copy()

# dataframe for clusterization model1: continous
cols = ['order_id', 'client_lat', 'client_lng', 'restaurant_lat',
        'restaurant_lng', 'price_with_discounts', 'delivey_fee', 'order_tip',
        'total_cost', 'hour', 'week_no', 'month', 'delivery_time', 'wait_lat',
        'wait_lng']
dforder_cluster1 = dforder_cluster[cols]

# dataframe for clusterization model2: categorical
cols2 = ['order_id', 'type_of_delivery', 'client_cat', 'price_cat',
         'cat_delivery', 'cat_payment', 'accepted_by_restaurant', 'cat_status',
         'cat_weekday', 'cat_month']
dforder_cluster2 = dforder_cluster[cols2]

"""
Define city and city limits: lat N, lat S, lng E, lng W

Example:
    Berkeley Extreme points
    37.90596, -122.27106
    37.84580, -122.27483
    37.87399, -122.32496
    37.8556, -122.23363
"""
N = 37.90596
S = 37.84580
E = -122.23363
W = -122.32496

city = dforder_cluster1[((dforder_cluster1['client_lat'] < N) & (dforder_cluster1['client_lat'] > S)) & \
                        (dforder_cluster1['wait_lat'] < N) & (dforder_cluster1['wait_lat'] > S) & \
                        ((dforder_cluster1['client_lng'] < E) & (dforder_cluster1['client_lng'] > W)) & \
                        (dforder_cluster1['wait_lng'] < E) & (dforder_cluster1['wait_lng'] > W) & \
                        (dforder_cluster1['total_cost'] > 0)]


################### Helper Functions for Elbow and K-means #################

def elbow_method(df=None):
    """Find the suggested number of clusters and plot the elbow diagram.

    args:
        df (pd.Dataframe): 2 columns dataframe

    returns:
        (k, fig) (int, go figure); (number of clusters, figure to plot)
    """

    row, cols = df.shape
    if cols != 2:
        raise ValueError("Dataframe must have 2 columns.")

    sum_sq_d = []
    K = list(range(1, 11))

    for k in K:
        km = KMeans(n_clusters=k)
        km = km.fit(df)
        sum_sq_d.append(km.inertia_)

    kl = KneeLocator(range(1, 11),
                     sum_sq_d,
                     curve="convex",
                     direction="decreasing")

    fig = go.Figure(data=go.Scatter(x=K, y=sum_sq_d))

    return kl.elbow, fig


def simple_cluster(K=1, df=None, add_col=False, col_name=None):
    """Create and assign cluster to each point of datadrame.

    args:
      K (int): number of clusters.
      df (pd.Dataframe): 2 columns dataframe to clusterize.
      add_col (bool): define if user wants to add a col in the df with
                      label values.
      col_name (str): name of the new df column.

    returns:
      go figure
    """
    row, cols = df.shape
    if cols != 2:
        raise ValueError("Dataframe must have 2 columns.")

        # Assign how many clusters (k-number) you would like to have
    K = K

    kmeans_model = KMeans(n_clusters=K, init='k-means++').fit(df)
    kmeans_model.inertia_

    # Iterative procedure to learn labels
    labels = kmeans_model.predict(df)

    if add_col is True and col_name is not None:
        df[col_name] = labels

    centroids = kmeans_model.cluster_centers_
    centroids = {i + 1: kmeans_model.cluster_centers_[i] for i in range(K)}

    color_map = {1: 'rgba(223,0,0,0.66)',
                 2: 'rgba(16,143,0,0.65)',
                 3: 'rgba(16,116,200,0.65)',
                 4: 'rgba(253,17,193,0.65)',
                 5: 'rgba(255,194,0,0.65)',
                 6: 'rgba(243,255,0,0.19)',
                 7: 'rgba(0,118,255,0.19)',
                 8: 'rgba(0,255,0,0.19)',
                 9: 'rgba(255,0,0,0.19)',
                 10: 'rgba(255,126,0,0.67)'}

    colors = [color_map[x + 1] for x in labels]

    fig = go.Figure()

    col1, col2 = df.columns

    fig.add_trace(
        go.Scatter(x=df[col1],
                   y=df[col2],
                   marker_color=colors)
    )

    for i in centroids.keys():
        fig.add_trace(go.Scatter(x=[centroids[i][0]],
                                 y=[centroids[i][1]],
                                 marker_size=10,
                                 marker_color=color_map[i]))

    fig.update_traces(mode='markers')

    return fig


##################################################################
###                   Continous Columns                        ###
##################################################################

################### Client Elbow #########################
################### Client Clusters ######################

################### Restaurants Elbow #########################
################### Restaurants Clusters ######################

################### Waiting Locations Elbow #########################
################### Waiting Locations Clusters ######################

##################################################################
###                  Categorial Columns                        ###
##################################################################

# Split data to train and text
np.random.seed(42)
ndata = len(dforder_cluster2)
idx_train = np.random.choice(range(ndata), int(0.8 * ndata), replace=False)
idx_test = np.asarray(list(set(range(ndata)) - set(idx_train)))
dfclus_train = dforder_cluster2.iloc[idx_train]  # the training data set
dfclus_test = dforder_cluster2.iloc[idx_test]  # the test data set

# Select columns to cluster
all_cols = ['type_of_delivery', 'client_cat', 'price_cat', 'cat_delivery',
            'cat_payment', 'accepted_by_restaurant', 'cat_status',
            'cat_weekday', 'cat_month']


# Clustering
def clustering(data, n_clusters):
    """ Performs K-mode clustering.
    args:
        data - cleaned dataset
        n_clusters - number of clusters
        algorithm - kmeans for numeric data; kmodes for categorical data
    returns:
        list, list: labels and centroids of clustering
    """
    clf = KModes(n_clusters=n_clusters,
                 init='Cao',
                 n_init=5,
                 verbose=0,
                 random_state=0)
    labels = clf.fit_predict(data)
    centroids = clf.cluster_centroids_

    return labels, centroids


# Interpreting
def interpret_clusters(df, labels, cols, method):
    df["labels"] = labels
    v_counts = df["labels"].value_counts()

    if method == "quantity":
        for i in set(labels):
            print(colored("\n Cluster {} - {}\n".format(i,
                                                        v_counts[i]),
                          color="magenta",
                          attrs=["bold"]))
            for c in cols:
                ls = df.loc[df['labels'] == i, c].value_counts()
                l = list(ls.index[0:2])
                v = ls.values[0:2]
                print(colored("{}:".format(c),
                              color="blue"), colored(l,
                                                     color="red",
                                                     attrs=["bold"]),
                      "-", v)
    if method == 'percentage':
        for i in set(labels):
            print(colored("\n Cluster {} - {}\n".format(i, v_counts[i]), color="magenta", attrs=["bold"]))
            for c in cols:
                ls = df.loc[df['labels'] == i, c].value_counts()
                all_ls = df[c].value_counts()[ls.index]
                ls = (ls / all_ls) * 100
                ls.sort_values(ascending=False, inplace=True)
                l = list(ls.index[0:2])
                v = np.round(ls, decimals=0).values[0:2]
                print(colored("{}:".format(c), color="blue"), colored(l, color="red", attrs=["bold"]), "-", v, "%")

            def plot_clusters(data, labels, centroids, int_method, title=''):
                # First we need to make 2D coordinates from the sparse matrix.
                customPalette = ["#2AB0E9", "#2BAF74", "#D7665E", "#CCCCCC",
                                 "#D2CA0D", "#522A64", "#A3DB05", "#FC6514"]

                pca = PCA(n_components=2).fit(data)
                coords = pca.transform(data)

                pca_data = pd.DataFrame()
                pca_data['PC1'] = coords[:, 0]
                pca_data['PC2'] = coords[:, 1]
                pca_data['label'] = labels
                pca_data['label'] = pca_data['label'].apply(lambda i: 'C' + str(i))

                # Plot the cluster centers
                centroid_coords = pca.transform(centroids)
                groups = {}
                for i in range(0, centroids.shape[0]):
                    groups['C' + str(i)] = centroid_coords[i]

                annots = []

                fig = tools.make_subplots(rows=1, cols=1, print_grid=False)

                for i, label in enumerate(groups.keys()):
                    ## Scatter Plot
                    trace1 = go.Scatter(x=pca_data.loc[pca_data['label'] == label, 'PC1'],
                                        y=pca_data.loc[pca_data['label'] == label, 'PC2'],
                                        mode='markers',
                                        name=label, marker=dict(size=12, color=customPalette[i]))

                    annot = dict(x=groups[label][0], y=groups[label][1], xref='x1', yref='y1', text=label,
                                 showarrow=False,
                                 font=dict(family='Courier New, monospace', size=16, color='#ffffff'),
                                 bordercolor='#c7c7c7', borderwidth=2, borderpad=4, bgcolor=customPalette[i], opacity=1)

                    annots.append(annot)
                    fig.append_trace(trace1, 1, 1)

                fig.layout.update(xaxis=dict(showgrid=False, title='PC1'), yaxis=dict(showgrid=False, title='PC2'),
                                  barmode='stack', annotations=annots, title=title + ' segmentation interest')
                iplot(fig)
                interpret_clusters(data_test, labels, all_cols, method=int_method)


# Performing clustering
data_test = dforder_cluster2.copy()
encoder = preprocessing.LabelEncoder()
data_test = data_test.apply(encoder.fit_transform)
data_test = data_test.drop(['order_id'], axis=1)

# Get the results
labels, centroids = clustering(data_test, n_clusters=2)

######################### Plot clusters ####################################
