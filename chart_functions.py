import plotly.express as px
import datetime
import pandas as pd
import numpy as np


def purchase_count(data):
    return np.count_nonzero(~np.isnan(data['date_purchased']))

def opportunity_count(purchase_data, opportunity_data):
    purchase_count = np.count_nonzero(~np.isnan(purchase_data['opportunity_created']))
    opportunity_count = np.count_nonzero(~np.isnan(opportunity_data['opportunity_created']))
    return purchase_count + opportunity_count

def win_rate(purchase_data, opportunity_data):
    purchase_count = np.count_nonzero(~np.isnan(purchase_data['opportunity_created']))
    opportunity_count = np.count_nonzero(~np.isnan(opportunity_data['opportunity_created']))
    return purchase_count / (purchase_count + opportunity_count)

def avg_sales_cycle(purchase_data):
    data = purchase_data.copy()
    data['time_delta'] = data['date_purchased'] - data['opportunity_created']
    return np.mean(data['time_delta']).days



# def fig_histogram(data, x_label, title):
#     fig = px.histogram(data, 
#                     x=x_label,
#                     histfunc='count',
#                     title=title)
#     fig.update_xaxes(categoryorder="total descending")
#     return fig