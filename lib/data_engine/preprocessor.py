import pandas as pd
import numpy as np
import os
import io
from datetime import datetime
from s3_get_object_all import df_kiwer, df_order


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
dforder.loc[(dforder['bot_name'] == 'kiwibot204') & (dforder['kiwer'].isnull())] = dforder.loc[(
    dforder['bot_name'] == 'kiwibot204') & (dforder['kiwer'].isnull())].fillna(value=values_1)
dforder = dforder.dropna(subset=['kiwer'])

# fill 0 values for nan
dforder[['client_lat', 'client_lng']] = dforder[[
    'client_lat', 'client_lng']].replace(0, np.NaN)

# replace value at restaunrat name fix typo of abbes pizza
dforder['restaurant_name'] = dforder['restaurant_name'].replace(
    'Abes pizza', "Abe's Pizza")

# fill nan in client_lat and client_lng
dforder = dforder.sort_values(by='client_readable_address')
dforder[['client_lat', 'client_lng']] = dforder[[
    'client_lat',	'client_lng']].ffill()
dforder = dforder.sort_values(by=['client_lat', 'client_lng'])
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
dforder['diff_closed'] = dforder['diff_closed'].dt.total_seconds()/60


# Setting up conditions to see if order was approved, error or canceled
conditions = [(((dforder['client_lat'] == dforder['restaurant_lat']) & (dforder['client_lng'] == dforder['restaurant_lng']) & (dforder['accepted_by_restaurant'].isna()))),
              (((dforder['client_lat'] != dforder['restaurant_lat']) & (dforder['client_lng']
                                                                        != dforder['restaurant_lng']) & (dforder['accepted_by_restaurant'].isna()))),
              ((dforder['load_battery'] == 100) &
               (dforder['wait_battery'] == 100)),
              (((dforder['load_battery'] == 100) & (dforder['wait_battery'] == 100)) & (dforder['accepted_by_restaurant'] is None))]
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
dfkiwer['weekday'] = pd.Categorical(dfkiwer['weekday'], categories=['Monday',
                                                                    'Tuesday',
                                                                    'Wednesday',
                                                                    'Thursday',
                                                                    'Friday',
                                                                    'Saturday',
                                                                    'Sunday'],
                                    ordered=True)

dfkiwer_days = dfkiwer['weekday'].value_counts(
    sort=False).rename_axis('Weekday').reset_index(name='Logs')


############ [Data Plot 2/7] Evolution of Weekdays ###############
# Create a dataframe with the groupby of weekday and month
multiple_weekday = dfkiwer.groupby(by=['weekday', 'month'], as_index=False)[
    'username'].count()

################ [Data Plot 3/7] Total logs by hour ################
# Create a dataframe with the kiwers total count per hours
dfkiwer_hours = dfkiwer['readable_datetime'].dt.hour.value_counts(
    sort=False).rename_axis('Hour').reset_index(name='Logs')

######## [Data Plot 4/7] Evolution of each hour by month ###############
# Create a dataframe of kiwers hours per month
dfkiwer['hour'] = dfkiwer['readable_datetime'].dt.hour
kiwers_hxm = dfkiwer.groupby(by=['hour', 'month'], as_index=False)[
    'username'].count()

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
           'delivey_fee', 'order_tax', 'order_tip',
           'delivery_time', 'load_battery',
           'wait_battery', 'total_cost', 'diff_closed',
           'hour', 'month']
y_list2 = ['client_is_prime', 'price_without_discounts', 'price_with_discounts',
           'delivey_fee', 'order_tax', 'order_tip',
           'delivery_time', 'load_battery',
           'wait_battery', 'total_cost', 'diff_closed',
           'hour', 'month']


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
dforder['weekday'] = pd.Categorical(dforder['weekday'], categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
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
dforder_res_mo = pd.pivot_table(dforder, index=['restaurant_name', 'month'], values=["client_is_prime"],
                                aggfunc=np.sum).fillna(0).reset_index().sort_values('restaurant_name')
dforder_res_mo.rename(columns={'client_is_prime': 'orders'})

################### Evolution of restaurants orders by week #################
dforder_res_week = pd.pivot_table(dforder, index=['restaurant_name', 'week_no'], values=["client_is_prime"],
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
dforder_accepted_mo = pd.pivot_table(dforder_accepted_mo, index=['restaurant_name', 'week_no', 'accepted_by_restaurant'],
                                     values=["client_is_prime"],
                                     aggfunc=np.sum).fillna(0).reset_index().sort_values(by=['restaurant_name', 'week_no'],
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

# dataframe for clusterization model1
cols = ['order_id', 'client_lat', 'client_lng', 'restaurant_lat',
        'restaurant_lng', 'price_with_discounts', 'delivey_fee', 'order_tip',
        'total_cost', 'hour', 'week_no', 'month', 'delivery_time', 'wait_lat',
        'wait_lng']
dforder_cluster1 = dforder_cluster[cols]

# dataframe for clusterization model2
cols2 = ['order_id', 'type_of_delivery', 'client_cat', 'price_cat',
         'cat_delivery', 'cat_payment', 'accepted_by_restaurant', 'cat_status',
         'cat_weekday', 'cat_month']
dforder_cluster2 = dforder_cluster[cols2]
