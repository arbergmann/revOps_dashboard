import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
from datetime import date
import chart_functions

def yoy_sales_chart(data):
    """ Year over year sales, trailing twelve months, + 3m forecast
    Arguments:
    data (DataFrame) -- purchase previously data loaded in from csv

    Returns:
    chart figure
    """
    # Initialize dates
    last_mth = pd.to_datetime(date.today() + relativedelta(months=-1, day=31)) # Get last day of previous month
    lookback = pd.to_datetime(date.today() + relativedelta(months=-13, day=31))
    prev_lookback_start = pd.to_datetime(date.today() + relativedelta(months=-13, day=31))
    prev_lookback_end =  pd.to_datetime(date.today() + relativedelta(months=-25, day=31))

    ttm = data[(data['date_purchased'] <= last_mth) & ((data['date_purchased'] > lookback))]
    prev_ttm = data[(data['date_purchased'] <= prev_lookback_start) & ((data['date_purchased'] > prev_lookback_end))]

    _1yr = ttm.groupby('month')['purchase_price'].sum()
    _2yr = prev_ttm.groupby('month')['purchase_price'].sum()

    # In filtering cases where the month has no sales, add 0 for that month
    months = list(range(1,13))
    _1yr_mths_needed = [x for x in months if x not in _1yr.index]
    _2yr_mths_needed = [x for x in months if x not in _2yr.index]

    if len(_1yr_mths_needed) > 0:
        _1yr_zeros = np.zeros(len(_1yr_mths_needed))
        _1yr_add = pd.Series(data=_1yr_zeros, index=_1yr_mths_needed)
        _1yr = pd.concat([_1yr, _1yr_add]).sort_index()
    
    if len(_2yr_mths_needed) > 0:
        _2yr_zeros = np.zeros(len(_2yr_mths_needed))
        _2yr_add = pd.Series(data=_2yr_zeros, index=_2yr_mths_needed)
        _2yr = pd.concat([_2yr, _2yr_add]).sort_index()

    # Set names for columns/legend later
    _1yr.name = 'ttm'
    _2yr.name = 'prev_ttm'

    # Get the months in the right order
    last_mth_idx = (date.today() + relativedelta(months=-1)).month
    _1yr = pd.concat([_1yr[last_mth_idx:], _1yr[:last_mth_idx]])
    _2yr = pd.concat([_2yr[last_mth_idx:], _2yr[:last_mth_idx]])

    _1yr.index = list(range(-12,0,1))
    _2yr.index = list(range(-12,0,1))

    ttm_all = pd.DataFrame(_1yr)
    ttm_all = pd.concat([ttm_all, _2yr], axis=1)
    ttm_all = ttm_all.reset_index().rename(columns={'index' : 'month_delta'})

    fig_yoy = go.Figure()
    # Add historical
    fig_yoy.add_trace(go.Scatter(x=ttm_all['month_delta'], y=ttm_all['ttm'], name="TTM", fill=None, line=dict(color='#4285F4', width=4)))
    fig_yoy.add_trace(go.Scatter(x=ttm_all['month_delta'], y=ttm_all['prev_ttm'], name="Previous TTM",  fill=None, opacity=.6, line=dict(color='#4285F4', dash='dot', width=4)))
    try:
        # Add predictions (lb, mean, ub), if possible
        arima_predictions = chart_functions.arima_predictions(data, ci=0.10)
        # Add a row with most recent data so that the charts connect, converging at point
        last_mth_row = pd.DataFrame({'month_delta' : -1, 'predicted_sales' : ttm_all['ttm'].tail(1), 
                                    'prediction_lower_bound' : ttm_all['ttm'].tail(1),
                                    'prediction_upper_bound' : ttm_all['ttm'].tail(1)})
        arima_predictions = pd.concat([last_mth_row, arima_predictions], axis=0)
        
        # Add to figure
        fig_yoy.add_trace(go.Scatter(x=arima_predictions['month_delta'], y=arima_predictions['prediction_lower_bound'], name='Predicted Sales Lower    ', 
                                    fill=None, opacity=0.2, line=dict(color='#224680', width=2)))
        fig_yoy.add_trace(go.Scatter(x=arima_predictions['month_delta'], y=arima_predictions['predicted_sales'], 
                                    fill='tonexty', name='Predicted Sales', line=dict(color='#224680', dash='dash', width=4)))
        fig_yoy.add_trace(go.Scatter(x=arima_predictions['month_delta'], y=arima_predictions['prediction_upper_bound'], name='Predicted Sales Upper    ',  
                                    fill='tonexty', opacity=0.2, line=dict(color='#224680', width=2)))
        fig_yoy.add_annotation(x=2, y=max(max(ttm_all['ttm']), max(ttm_all['prev_ttm'])), showarrow=False,
                               text=f'Forecasting CI: 90%')
    except:
        # If not possible, will just leave one level up of charts
        fig_yoy.add_annotation(x=-1, y=max(max(ttm_all['ttm']), max(ttm_all['prev_ttm'])), showarrow=False,
                               text=f'Forecasting not<br>available for<br>{make_value} : {model_value}')
        pass
    fig_yoy.update_layout(title_text='Year-over-Year Sales and 3-Month Forecast ($)', title_x = 0.5, 
                          xaxis_title='Month Delta', yaxis_title='Total Sales ($)',
                          annotations=[go.layout.Annotation(xanchor='right', yanchor='top')])

    return fig_yoy



def sales_distribution_histogram(make_value, model_value, data):
    """ Distribution of sales by make, model
    Arguments:
    make_value (str) -- dropdown make value to filter on
    model_value (str) -- dropdown model value to filter on
    data (DataFrame) -- purchase data previously loaded in from csv

    Returns:
    chart figure
    """
    if ((make_value is None) and (model_value is None)) | ((make_value is None) and (model_value is not None)):
        fig_hist = px.histogram(data, 
                    x="car_make",
                    histfunc='count',
                    color_discrete_sequence=['#4287F5'])
        fig_hist.update_xaxes(categoryorder="total descending", title='Make')
        fig_hist.update_layout(title_text='Sales by Make (#)', title_x = 0.5, 
                               xaxis_title='Make', yaxis_title='# Sold')

    elif (make_value is not None) and (model_value is None):
        fig_hist = px.histogram(data, 
                    x="car_model",
                    histfunc='count',
                    color_discrete_sequence=['#4287F5'])
        fig_hist.update_xaxes(categoryorder="total descending")
        fig_hist.update_layout(title_text='Sales by Model (#)', title_x = 0.5, 
                               xaxis_title='Model', yaxis_title='# Sold')

    else:
        fig_hist = px.histogram(data, 
                    x="month",
                    histfunc='count',
                    color_discrete_sequence=['#4287F5'])
        fig_hist.update_xaxes(categoryorder="total descending")
        fig_hist.update_layout(title_text='Sales by Month (#)', title_x = 0.5, 
                               xaxis_title='Month', yaxis_title='# Sold')

    return fig_hist



def sunburst_chart(data, pth):
    """ Sunburst breakdown, by make/model.
    Arguments:
    data (DataFrame) -- purchase data previously loaded in from csv
    pth (list) -- path of sunburst chart from inside to outside

    Returns:
    chart figure
    """
    fig_sburst = px.sunburst(data, 
                    path=pth, 
                    values='purchase_price', 
                    color_continuous_scale=['#FFFFFF', '#4285F4', '#224680'], # Not working...?
                    )
    fig_sburst.update_layout(title_text='Sales Breakdown by Type (%)', title_x = 0.5)

    return fig_sburst



def sales_metrics_tables(make_value, data):
    """ Tables of top 5 sales, top 5 counts
    Arguments:
    make_value (str) -- make value to filter on
    data (DataFrame) -- purchase data previously loaded in from csv

    Returns:
    chart figure
    """
    if make_value == None:
        top_5_sales = data.groupby('car_make')['purchase_price'].sum().sort_values(ascending=False).head(10).apply(lambda x: f"${x/1000:,.0f}k")\
                        .reset_index().rename(columns={'car_make' : 'Car Make', 'purchase_price' : 'Top 10 Total Sales'})
        top_5_count = data.groupby('car_make')['purchase_price'].count().sort_values(ascending=False).head(10)\
                        .reset_index().rename(columns={'car_make' : 'Car Make', 'purchase_price' : 'Top 10 Total Count'})
    else:
        top_5_sales = data.groupby('car_model')['purchase_price'].sum().sort_values(ascending=False).head(10).apply(lambda x: f"${x/1000:,.0f}k")\
                        .reset_index().rename(columns={'car_model' : 'Car Model', 'purchase_price' : 'Top 10 Total Sales'})
        top_5_count = data.groupby('car_model')['purchase_price'].count().sort_values(ascending=False).head(10)\
                        .reset_index().rename(columns={'car_model' : 'Car Model', 'purchase_price' : 'Top 10 Total Count'})

    return top_5_sales, top_5_count