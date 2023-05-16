#%%
from dash import Dash, html, dcc, State
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import sys, os
import chart_functions
import tools

purchases, opportunities, competitors = tools.load_data()

#%%

# data = purchases.copy()

def avg_sales_cycle(purchase_data):
    data = purchase_data.copy()
    data['time_delta'] = data['date_purchased'] - data['opportunity_created']
    return np.mean(data['time_delta']).days

# %%
