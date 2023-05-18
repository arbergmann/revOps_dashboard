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

competitor_meds = pd.DataFrame(competitors.groupby('car_make')['purchase_price'].median()).rename(columns={'purchase_price':'Competitor Median'})
purchase_avgs = pd.DataFrame(purchases.groupby(['car_make']).agg({'purchase_price' : [np.mean, 'count']}).droplevel(axis=1, level=0)).rename(columns={'mean': 'Average Price', 'count':'Count'})

pricing_deltas = pd.concat([competitor_meds, purchase_avgs], axis=1, join='inner', ignore_index=False)
pricing_deltas['pricing_delta'] = pricing_deltas['Average Price'] - pricing_deltas['Competitor Median']
pricing_deltas['pricing_delta_pct'] = pricing_deltas['Average Price'] / pricing_deltas['Competitor Median'] - 1
pricing_deltas.sort_values('pricing_delta_pct', ascending=True, inplace=True)
pricing_deltas['Opportunity Cost'] = pricing_deltas['pricing_delta'] * pricing_deltas['Count']
pricing_deltas = pricing_deltas.rename(columns={'pricing_delta_pct' : 'Pricing Delta (%)', 'pricing_delta' : 'Pricing Delta ($)'}).head(10)

pricing_deltas

# %%

financials.iloc[:,-1]
# %%
