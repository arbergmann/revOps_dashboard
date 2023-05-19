#%%
from dash import Dash, html, dcc, State
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import sys, os
import chart_functions
import tools

# Load Data
purchases, opportunities, competitors, financials = tools.load_data()

#%%

data_p = purchases.copy()
data_o = opportunities.copy()
data_f = financials.copy()

mth_q_dict = {1 : "_q1", 2 : "_q1", 3 : "_q1",
              4 : "_q2", 5 : "_q2", 6 : "_q2",
              7 : "_q3", 8 : "_q3", 9 : "_q3",
              10 : "_q4", 11 : "_q4", 12 : "_q4"}


new_customer_count = data_p.groupby(['year', 'month'])['date_purchased'].count().reset_index()
new_customer_count['quarter'] = new_customer_count['year'].apply(lambda x: str(x)) + new_customer_count['month'].apply(lambda x: mth_q_dict[x])
new_customer_count = new_customer_count.groupby('quarter')['date_purchased'].sum()

marketing_exp = data_f.T['marketing']
marketing_exp

cust_acq_cost = pd.concat([new_customer_count,marketing_exp], axis=1, join='inner')
cust_acq_cost['customer_acquisition_cost'] = cust_acq_cost.marketing / cust_acq_cost.date_purchased

if cust_acq_cost['marketing'][-1] > cust_acq_cost['marketing'][-2]:
    trend_qoq = """HIGHER"""
elif cust_acq_cost['marketing'][-1] < cust_acq_cost['marketing'][-2]:
    trend_qoq = """LOWER"""
else:
    trend_qoq = """FLAT"""

if cust_acq_cost['marketing'][-1] > cust_acq_cost['marketing'][-5]:
    trend_yoy = """HIGHER"""
elif cust_acq_cost['marketing'][-1] < cust_acq_cost['marketing'][-5]:
    trend_yoy = """LOWER"""
else:
    trend_yoy = """FLAT"""


fig_cust_cost = px.line(cust_acq_cost, x=cust_acq_cost.index, y='customer_acquisition_cost')
fig_cust_cost

#%%
cust_acq_cost['marketing'][-5]


# %%


# # Trailing Twelve Months Win Rate BY MAKE/MODEL
# ttm_data_p = data_p.copy()
# ttm_data_o = data_o.copy()
# # ttm_data_p['label'] = ttm_data_p['year'].apply(lambda x: str(x)) + '_' + ttm_data_p['month'].apply(lambda x: str(x))
# # ttm_data_o['label'] = ttm_data_o['year'].apply(lambda x: str(x)) + '_' + ttm_data_o['month'].apply(lambda x: str(x))

# # Get total counts for each month
# ttm_purch = ttm_data_p.groupby(['year', 'month', 'car_make'])['date_purchased'].count().reset_index()
# ttm_opps = ttm_data_o.groupby(['year', 'month', 'car_make_interest'])['opportunity_created'].count().reset_index()

# purch_idx = ttm_purch[['year','month']]
# purch_idx.index.rename('level_1', inplace=True)
# purch_idx.reset_index(inplace=True)

# # Get rolling sum for each month - purchases=6m, opportunities=12m
# # ttm_purch['rolling_purchases'] = ttm_purch['date_purchased'].groupby(ttm_purch['car_make']).transform(sum)
# # ttm_purch = ttm_purch.groupby('car_make').rolling(6)['date_purchased'].sum().reset_index()
# # ttm_opps['rolling_opportunities'] = ttm_opps['opportunity_created'].rolling(12).sum()

# # purch_idx
# ttm_purch[ttm_purch['car_make'] == 'Acura']