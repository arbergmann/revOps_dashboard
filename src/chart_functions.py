import plotly.express as px
import datetime
import pandas as pd
import numpy as np


def purchase_count(data):
    """ Calculate the count of purchases made.
    Arguments:
    data (DataFrame) -- purchase previously data loaded in from csv

    Returns:
    purchase count (int) -- a count of the purchases
    """
    return np.count_nonzero(~np.isnan(data['date_purchased']))

def opportunity_count(purchase_data, opportunity_data):
    """ Calculate the count of purchases made.
    Arguments:
    purchase_data (DataFrame) -- purchase data previously loaded in from csv
    opportunity_data (DataFrame) -- opportunity data previously loaded in from csv

    Returns:
    total opportunity count (int) -- a count of the total opportunities (in this case, 
                                     purchases include their respective opportunities)
    """
    purchase_count = np.count_nonzero(~np.isnan(purchase_data['opportunity_created']))
    opportunity_count = np.count_nonzero(~np.isnan(opportunity_data['opportunity_created']))
    return purchase_count + opportunity_count

def win_rate(purchase_data, opportunity_data):
    """ Calculate the win rate.
    Arguments:
    purchase_data (DataFrame) -- purchase data previously loaded in from csv
    opportunity_data (DataFrame) -- opportunity data previously loaded in from csv

    Returns:
    win rate (float) -- win rate as decimal pct (purchases / total opportunities)
    """
    purchase_count = np.count_nonzero(~np.isnan(purchase_data['opportunity_created']))
    opportunity_count = np.count_nonzero(~np.isnan(opportunity_data['opportunity_created']))
    return purchase_count / (purchase_count + opportunity_count)

def avg_sales_cycle(purchase_data):
    """ Calculate the average sales cycle time.
    Arguments:
    purchase_data (DataFrame) -- purchase data previously loaded in from csv

    Returns:
    average sales cycle days (int) -- a count of the average days from opportunity to purchase.
    """
    data = purchase_data.copy()
    data['time_delta'] = data['date_purchased'] - data['opportunity_created']
    return np.mean(data['time_delta']).days
