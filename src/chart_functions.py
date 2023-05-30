#%%
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from statsmodels.tsa.arima.model import ARIMA, ARIMAResults
from warnings import catch_warnings, filterwarnings
import pandas as pd
import numpy as np

"""
The code for the app.py can be quite cumbersome as it is managing an entire app.

So, to clean up the code a little bit, I have implemented some functions here
that act as helper functions for various charts and markdowns, that will help 
to condense the other code a little bit.
"""

def purchase_count(data):
    """ Calculate the count of purchases made.
    Arguments:
    data (DataFrame) -- purchase previously data loaded in from csv

    Returns:
    purchase count (int) -- a count of the purchases
    """
    trailing_6m = data[data['date_purchased'] > pd.to_datetime(date.today() + relativedelta(months=-6))]
    return np.count_nonzero(~np.isnan(trailing_6m['date_purchased']))

def opportunity_count(purchase_data, opportunity_data):
    """ Calculate the count of opportunities. We have to pull in purchase data because their opportunity data
    exists only in the purchase dataset.
    Arguments:
    purchase_data (DataFrame) -- purchase data previously loaded in from csv
    opportunity_data (DataFrame) -- opportunity data previously loaded in from csv

    Returns:
    total opportunity count (int) -- a count of the total opportunities (in this case, 
                                     purchases include their respective opportunities)
    """
    trailing_6m_pur = purchase_data[purchase_data['date_purchased'] > pd.to_datetime(date.today() + relativedelta(months=-6))]
    trailing_6m_opp = opportunity_data[opportunity_data['opportunity_created'] > pd.to_datetime(date.today() + relativedelta(months=-6))]
    
    purchase_count = np.count_nonzero(~np.isnan(trailing_6m_pur['date_purchased']))
    opportunity_count = np.count_nonzero(~np.isnan(trailing_6m_opp['opportunity_created']))
    return purchase_count + opportunity_count

def win_rate(purchase_data, opportunity_data):
    """ Calculate the win rate. Since we don't define closing of an opportunity here,
    we will just use TTM opportunities.
    Arguments:
    purchase_data (DataFrame) -- purchase data previously loaded in from csv
    opportunity_data (DataFrame) -- opportunity data previously loaded in from csv

    Returns:
    win rate (float) -- win rate as decimal pct (purchases / total opportunities)
    """
    trailing_6m_pur = purchase_data[purchase_data['date_purchased'] > pd.to_datetime(date.today() + relativedelta(months=-6))]
    trailing_12m_opp = opportunity_data[opportunity_data['opportunity_created'] > pd.to_datetime(date.today() + relativedelta(months=-12))]
    
    purchase_count = np.count_nonzero(~np.isnan(trailing_6m_pur['date_purchased']))
    opportunity_count = np.count_nonzero(~np.isnan(trailing_12m_opp['opportunity_created']))
    return purchase_count / (purchase_count + opportunity_count)

def avg_sales_cycle(purchase_data):
    """ Calculate the TTM average sales cycle time.
    Arguments:
    purchase_data (DataFrame) -- purchase data previously loaded in from csv

    Returns:
    average sales cycle days (int) -- a count of the average days from opportunity to purchase.
    """
    data = purchase_data[purchase_data['date_purchased'] > pd.to_datetime(date.today() + relativedelta(months=-6))].copy()
    data['time_delta'] = data['date_purchased'] - data['opportunity_created']
    return np.mean(data['time_delta']).days

def index_list(purchase_data):
    """ Gets index list of month/year combinations
    Arguments:
    purchase_data (DataFrame) -- purchase data previously loaded in from csv

    Returns:
    index list (list) -- List of year/month combinations
    """
    
    data = purchase_data.groupby(['year','month'])['purchase_price'].sum().reset_index()
    for col in ['year','month']:
        data[col] = data[col].apply(lambda x: str(x))
    data['idx'] = data.year.str.cat(data.month, sep='-')
 
    return list(data.idx)

def arima_predictions(purchase_data, ci=0.05):
    """ Predict sales for 6 months out with confidence interval using past purchase data.
    Arguments:
    purchase_data (DataFrame) -- purchase data previously loaded in from csv

    Returns:
    arima_preds (DataFrame) -- arima predictions with confidence interval.
    """
    
    data = purchase_data.groupby(['year','month'])['purchase_price'].sum().reset_index()
    for col in ['year','month']:
        data[col] = data[col].apply(lambda x: str(x))
    data['idx'] = data.year.str.cat(data.month, sep='-')
    data.set_index('idx', inplace=True)
    data = data['purchase_price']
    # print(len(data))
    
    # Fill in any blanks in index
    reqd_indices = index_list(purchase_data)
    months = list(range(1,42))
    months_needed = [x for x in reqd_indices if x not in list(data.index)]

    if len(months_needed) > 0:
        mths_zeros = np.zeros(len(months_needed))
        mths_to_add = pd.Series(data=mths_zeros, index=months_needed)
        data = pd.concat([data, mths_to_add]).sort_index()

    # If today's date isn't the first, drop any data from this month
    # to prevent incomplete data from messing with model
    if date.today().day != 1:
        data = data[:-1]

    arima = ARIMA(data, order=(1,0,3))
    model = arima.fit()
    forecast = model.get_forecast(steps=3)
    preds_mean = forecast.predicted_mean
    preds_ci = forecast.conf_int(alpha=ci)

    preds = pd.concat([preds_mean, preds_ci], axis=1)
    preds['month_delta'] = [0, 1, 2]
    preds.rename(columns={'predicted_mean' : 'predicted_sales', 
                          'lower purchase_price':'prediction_lower_bound',
                          'upper purchase_price':'prediction_upper_bound'}, 
                 inplace=True)

    return preds