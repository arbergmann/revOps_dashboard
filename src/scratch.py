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

purchases, opportunities, competitors = tools.load_data()

#%%

data_p = purchases.copy()
data_c = competitors.copy()


def fig_competitor(make_value, model_value):
    if (make_value is None) and (model_value is None):
        data_p = purchases.copy()
        data_c = competitors.copy()

        # Plot competitor data
        fig = px.box(data_c, x='car_make', y='purchase_price')
        
        # plot user data....
        # fig.layout.xaxis2 = go.layout.XAxis(overlaying='x', range=[0,1], showticklabels=False)
        # fig.add_scatter(x = [0, 1], y=[....figure out how to provide for each different product])
        # likely requires a for loop, i.e.:
        # for col in df:
            # fig.add_trace....

    elif (make_value is not None) and (model_value is None):
        data_p = purchases[purchases['car_make'] == make_value]
        data_c = competitors[competitors['car_make'] == make_value]

        fig = px.box(data_c, x='car_model', y='purchase_price')

    else:
        data_p = competitors[(competitors['car_make'] == make_value) & (competitors['car_model'] == model_value)]
        data_c = competitors[(competitors['car_make'] == make_value) & (competitors['car_model'] == model_value)]

        fig = px.box(data_c, x='car_model', y='purchase_price')

    return fig

fig_competitor(make_value=None, model_value=None)
# fig_competitor(make_value='Ford', model_value=None)
# fig_competitor(make_value='Ford', model_value='Bronco II')
# %%
