import plotly.express as px
import pandas as pd
import numpy as np


def purchase_count(data):
    return np.count_nonzero(~np.isnan(data['date_purchased']))

def opportunity_count(purchase_data, opportunity_data):
    purchase_count = np.count_nonzero(~np.isnan(purchase_data['opportunity_created']))
    opportunity_count = np.count_nonzero(~np.isnan(opportunity_data['opportunity_created']))
    return purchase_count + opportunity_count

# def win_rate()

def fig_histogram(data, x=''):
    fig = px.histogram(data, x=x, title="Sales by Model/Make")
    fig.update_xaxes(categoryorder="total descending")
    return fig

