import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
from datetime import date

def ttm_sales_cycle_days(data_p):
    """ Chart the sales cycle days, trailing twelve months
    Arguments:
    data_p (DataFrame) -- purchase data previously loaded in from csv

    Returns:
    chart figure
    """
    ttm_data = data_p.copy()
    ttm_data['time_delta'] = ttm_data['date_purchased'] - ttm_data['opportunity_created']
    ttm_data['time_delta'] = ttm_data['time_delta'].apply(lambda x: x.days)
    
    ttm_sales = ttm_data.groupby(['year', 'month'])['time_delta'].mean().reset_index()
    ttm_sales = ttm_sales.tail(12)
    ttm_sales['label'] = ttm_sales['year'].apply(lambda x: str(x)) + '_' + ttm_sales['month'].apply(lambda x: str(x))
    
    fig_ttm_cycle = go.Figure()
    fig_ttm_cycle.add_trace(go.Scatter(x=ttm_sales['label'], y=ttm_sales['time_delta'], 
                                       fill=None, mode='lines', line=dict(color='#4285F4', width=4)))
    fig_ttm_cycle.update_layout(title_text='TTM Sales Cycle Trend', title_x = 0.5, 
                          xaxis_title='Month', yaxis_title='TTM Sales Cycle Days')

    return fig_ttm_cycle


def ttm_sales_cycle_strip(make_value, data_p):
    """ Chart the sales cycle days, trailing twelve months, distribution breakdown by make/model
    Arguments:
    make_value (str) -- dropdown value of car make
    data_p (DataFrame) -- purchase data previously loaded in from csv

    Returns:
    chart figure
    """
    ttm_data = data_p.copy()
    ttm_data['time_delta'] = ttm_data['date_purchased'] - ttm_data['opportunity_created']
    ttm_data['time_delta'] = ttm_data['time_delta'].apply(lambda x: x.days)

    if make_value == None:
        ttm_sales = ttm_data[(ttm_data['date_purchased'] <= pd.to_datetime(date.today())) & (ttm_data['date_purchased'] >= pd.to_datetime(date.today() + relativedelta(months=-13)))]
        fig_strip_sales = px.strip(ttm_sales, x='time_delta', y='car_make', color_discrete_sequence=["#4287F5"])
        fig_strip_sales.update_layout(title_text='TTM Sales Cycle by Make', title_x = 0.5, 
                          xaxis_title='TTM Sales Cycle Days', yaxis_title='Car Make')
    else:
        ttm_sales = ttm_data[(ttm_data['date_purchased'] <= pd.to_datetime(date.today())) & (ttm_data['date_purchased'] >= pd.to_datetime(date.today() + relativedelta(months=-13)))]
        fig_strip_sales = px.strip(ttm_sales, x='time_delta', y='car_model', color_discrete_sequence=["#4287F5"])
        fig_strip_sales.update_layout(title_text='TTM Sales Cycle by Model', title_x = 0.5, 
                          xaxis_title='TTM Sales Cycle Days', yaxis_title='Car Model')
        
    return fig_strip_sales


def ttm_win_rate(data_p, data_o):
    """ Chart the win rate, month-by-month
    Arguments:
    data_p (DataFrame) -- purchase data previously loaded in from csv
    data_o (DataFrame) -- opportunity data previously loaded in from csv

    Returns:
    chart figure
    """
    ttm_data_p = data_p.copy()
    ttm_data_o = data_o.copy()

    # Get total counts for each month
    ttm_purch = ttm_data_p.groupby(['year','month'])['date_purchased'].count().reset_index()
    ttm_opps = ttm_data_o.groupby(['year','month'])['opportunity_created'].count().reset_index()

    # Get rolling sum for each month - purchases=6m, opportunities=12m
    ttm_purch['rolling_purchases'] = ttm_purch['date_purchased'].rolling(6).sum()
    ttm_opps['rolling_opportunities'] = ttm_opps['opportunity_created'].rolling(12).sum()

    # Get win rates
    ttm_winrt = pd.merge(ttm_purch, ttm_opps, how='outer', on=['year','month']).sort_values(by=['year','month'])
    ttm_winrt['win_rt'] = ttm_winrt['rolling_purchases'] / (ttm_winrt['rolling_purchases'] + ttm_winrt['rolling_opportunities']) * 100
    ttm_winrt = ttm_winrt.tail(12)
    ttm_winrt['label'] = ttm_winrt['year'].apply(lambda x: str(x)) + '_' + ttm_winrt['month'].apply(lambda x: str(x))

    fig_ttm_winrt = px.line(ttm_winrt, x='label', y='win_rt')
    fig_ttm_winrt.update_layout(title_text='TTM Win Rate', title_x = 0.5, 
                          xaxis_title='Month', yaxis_title='Win Rate (%)')

    fig_ttm_winrt = go.Figure()
    fig_ttm_winrt.add_trace(go.Scatter(x=ttm_winrt['label'], y=ttm_winrt['win_rt'], 
                                       fill=None, mode='lines', line=dict(color='#4285F4', width=4)))
    fig_ttm_winrt.update_layout(title_text='Win Rate by Month', title_x = 0.5, 
                            xaxis_title='Quarter', yaxis_title='Win Rate (%)')

    return fig_ttm_winrt


def customer_acq_cost(data_p, financials):
    """ Chart the customer acquisition cost by quarter
    Arguments:
    make_value (str) -- dropdown value of car make
    data_p (DataFrame) -- purchase data previously loaded in from csv

    Returns:
    chart figure
    """
    mth_q_dict = {1 : "_q1", 2 : "_q1", 3 : "_q1",
            4 : "_q2", 5 : "_q2", 6 : "_q2",
            7 : "_q3", 8 : "_q3", 9 : "_q3",
            10 : "_q4", 11 : "_q4", 12 : "_q4"}

    new_customer_count = data_p.groupby(['year', 'month'])['date_purchased'].count().reset_index()
    new_customer_count['quarter'] = new_customer_count['year'].apply(lambda x: str(x)) + new_customer_count['month'].apply(lambda x: mth_q_dict[x])
    new_customer_count = new_customer_count.groupby('quarter')['date_purchased'].sum()

    marketing_exp = financials.T['marketing']

    cust_acq_cost = pd.concat([new_customer_count,marketing_exp], axis=1, join='inner')
    cust_acq_cost['customer_acquisition_cost'] = cust_acq_cost.marketing / cust_acq_cost.date_purchased

    # Markdown Outputs
    if cust_acq_cost['marketing'][-1] > cust_acq_cost['marketing'][-2]:
        trend_qoq = """HIGHER"""
        trend_qoq_color = "red"
    elif cust_acq_cost['marketing'][-1] < cust_acq_cost['marketing'][-2]:
        trend_qoq = """LOWER"""
        trend_qoq_color = "green"
    else:
        trend_qoq = """FLAT"""
        trend_qoq_color = "grey"

    if cust_acq_cost['marketing'][-1] > cust_acq_cost['marketing'][-5]:
        trend_yoy = """HIGHER"""
        trend_yoy_color = "red"
    elif cust_acq_cost['marketing'][-1] < cust_acq_cost['marketing'][-5]:
        trend_yoy = """LOWER"""
        trend_yoy_color = "green"
    else:
        trend_yoy = """FLAT"""
        trend_yoy_color = "grey"

    fig_cust_cost = go.Figure()
    fig_cust_cost.add_trace(go.Scatter(x=cust_acq_cost.index, y=cust_acq_cost['customer_acquisition_cost'], 
                                       fill=None, mode='lines', line=dict(color='#4285F4', width=4)))
    fig_cust_cost.update_layout(title_text='Customer Acquisition Cost by Quarter', title_x = 0.5, 
                            xaxis_title='Quarter', yaxis_title='Customer Acquisition Cost ($)')

    return fig_cust_cost, trend_yoy, trend_qoq, trend_yoy_color, trend_qoq_color