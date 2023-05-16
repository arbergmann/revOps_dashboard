#%%
from dash import Dash, html, dcc, Input, Output, State
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
purchases, opportunities, competitors = tools.load_data()

# Spin up app
stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=stylesheet)

app.layout = html.Div([
    html.H1("RevOps Dashboard for Used Car Sales", style={"textAlign":"center"}),

    ## Bring in statistics
    html.Hr(),
    html.H2("Overall Statistics", style={"textAlign" : "center"}),
    html.Div([
        html.Div([dcc.Markdown("""
                ### Total Purchases
                ###### {}
                """.format(str(chart_functions.purchase_count(purchases))),
                style={"textAlign" : "center"})],
                className="three columns"),
        html.Div([dcc.Markdown("""
                ### Total Opportunities
                ###### {}
                """.format(str(chart_functions.opportunity_count(purchases, opportunities))), 
                style={"textAlign" : "center"})],
                className="three columns"),
        html.Div([dcc.Markdown("""
                ### Total Win Rate
                ###### {:.2%}
                """.format(chart_functions.win_rate(purchases, opportunities)),
                style={"textAlign" : "center"})],
                className="three columns"),
        html.Div([dcc.Markdown("""
                #### Trailing 6m Sales 
                #### Cycle Length
                ###### {} Days
                """.format(chart_functions.avg_sales_cycle(purchases)),
                style={"textAlign" : "center"})],
                className="three columns")
    ], className="row"),

     ## Car make filter
    html.Hr(),
    html.P("Filter by car make (optional): "),
    html.Div(html.Div([
        dcc.Dropdown(id='make_dd', 
                     clearable=True, 
                     value=None,
                     options=[{'label' : i, "value" : i} for i in sorted(purchases['car_make'].unique())]),
    ], className="two columns"), className="row"),

    ## Car Model filter
    html.P("Filter by car model (optional): "),
    html.Div(html.Div([
        dcc.Dropdown(id='model_dd', 
                    clearable=True, 
                    value=None)
    ], className="two columns"), className="row"),


    ## Bring in charts
    # html.Div(id='outputDiv', children=[]),

    # Testing feed-through of filters
    # html.Hr(),
    # html.Div([
    #     html.Div([dcc.Markdown(id='testing')], className="six columns"),
    # ], className="row"),

    ## Sales Metrics
    html.Hr(),
    html.H2("Sales Metrics", style={"textAlign" : "center"}),
    html.Div([
        html.Div([dcc.Graph(id='fig_hist')], className="six columns"),
        html.Div([dcc.Graph(id='fig_qoq_sales')], className="six columns"),
    ], className="row"),
    html.Div([
        html.Div([dcc.Graph(id='sunburst')], className="six columns"),
    ], className="row"),

    ## Sales Lifecycle
    html.Hr(),
    html.H2("Sales Lifecycle", style={"textAlign" : "center"}),

    ## Competitor Analysis
    html.Hr(),
    html.H2("Competitor Analysis", style={"textAlign" : "center"}),
    html.Div([
        html.Div([dcc.Graph(id='competitor_product')], className="six columns"),
    ], className="row"),
])

## Callback for dropdown
@app.callback(Output(component_id='model_dd', component_property='options'),
              Input(component_id='make_dd', component_property='value'))
def update_model_dd(make_value):
    if make_value is None:
        return [{'label' : i, "value" : i} for i in sorted(purchases['car_model'].unique())]
    else:
        data = purchases[purchases['car_make'] == make_value]
        return [{'label' : i, "value" : i} for i in sorted(data['car_model'].unique())]


########################
### Chart Generation ###
########################

# # Testing
# @app.callback(Output(component_id='testing', component_property='children'),
#               Input(component_id='make_dd', component_property='value'),
#               Input(component_id='model_dd', component_property='value'))
# def test_func(make_value, model_value):
    
#     output = f"""
#     Testing output:
#     Make: {make_value}
#     Model: {model_value}
#     """

#     return output

## Histogram
@app.callback(Output(component_id='fig_hist', component_property='figure'),
              Input(component_id='make_dd', component_property='value'),
              Input(component_id='model_dd', component_property='value'))
def fig_histogram(make_value, model_value):
    if (make_value is None) and (model_value is None):
        data = purchases.copy()
        fig = px.histogram(data, 
                    x="car_make",
                    histfunc='count',
                    title="Sales by Make")
        fig.update_xaxes(categoryorder="total descending")
        return fig

    elif (make_value is not None) and (model_value is None):
        data = purchases[purchases['car_make'] == make_value]
        fig = px.histogram(data, 
                    x="car_model",
                    histfunc='count',
                    title="Sales by Model")
        fig.update_xaxes(categoryorder="total descending")
        return fig

    else:
        data = purchases[(purchases['car_make'] == make_value) & (purchases['car_model'] == model_value)]
        fig = px.histogram(data, 
                    x="month",
                    histfunc='count',
                    title="Sales by Month")
        fig.update_xaxes(categoryorder="total descending")
        return fig


## Quarter-over-Quarter Sales
@app.callback(Output(component_id='fig_qoq_sales', component_property='figure'),
              Input(component_id='make_dd', component_property='value'),
              Input(component_id='model_dd', component_property='value'))
def fig_qoq_sales(make_value, model_value):
    if (make_value is None) and (model_value is None):
        data = purchases.copy()
    elif (make_value is not None) and (model_value is None):
        data = purchases[purchases['car_make'] == make_value]
    else:
        data = purchases[(purchases['car_make'] == make_value) & (purchases['car_model'] == model_value)]

    # Initialize dates
    curr_mth = date.today() + relativedelta(months=-1)
    lookback = date.today() + relativedelta(months=-3)
    prev_lookback_start = date.today() + relativedelta(months=-6)
    prev_lookback_end =  date.today() + relativedelta(months=-4)

    curr_range = list(pd.period_range(lookback, curr_mth, freq='M'))
    curr_range = [x.month for x in curr_range]

    prev_range = list(pd.period_range(prev_lookback_start, prev_lookback_end, freq='M'))
    prev_range = [x.month for x in prev_range]
    prev_range

    # It is understood that these will result in numerically incorrect outputs
    # (i.e. it will sort 1, 11, 12, as oppsoed to looking back at 11, 12, 1 in that order)
    # For the sake of time and just getting a visual in place on mock data, I will ignore this for now.
    three_month = data[data['month'].isin(curr_range)].groupby('month')['purchase_price'].sum()
    prev_three_mth = data[data['month'].isin(prev_range)].groupby('month')['purchase_price'].sum()
    three_month.name = 'most_recent_quarter'
    prev_three_mth.name = 'prev_quarter'

    three_month.index = [-3,-2,-1]
    prev_three_mth.index = [-3,-2,-1]

    three_month = pd.DataFrame(three_month)
    three_month = pd.concat([three_month, prev_three_mth], axis=1)
    three_month = three_month.reset_index().rename(columns={'index' : 'month_delta'})

    # Generate plot
    fig = px.line(three_month, 
                  x='month_delta', 
                  y=['most_recent_quarter', 'prev_quarter'], 
                  title='Quarter-over-Quarter Sales ($)')
    return fig


## Sunburst Breakdown
@app.callback(Output(component_id='sunburst', component_property='figure'),
              Input(component_id='make_dd', component_property='value'),
              Input(component_id='model_dd', component_property='value'))
def fig_sunburst(make_value, model_value):
    if (make_value is None) and (model_value is None):
        data = purchases.copy()
        pth = ['car_make', 'car_model', 'car_year']
    elif (make_value is not None) and (model_value is None):
        data = purchases[purchases['car_make'] == make_value]
        pth = ['car_model', 'car_year', 'car_color']
    else:
        data = purchases[(purchases['car_make'] == make_value) & (purchases['car_model'] == model_value)]
        pth = ['car_model', 'car_year', 'car_color']

    fig = px.sunburst(data, 
                      path=pth, 
                      values='purchase_price', 
                      title='Sales Breakdown by Type')
    return fig


## Competitor Analysis Breakdown
@app.callback(Output(component_id='competitor_product', component_property='figure'),
              Input(component_id='make_dd', component_property='value'),
              Input(component_id='model_dd', component_property='value'))
def fig_competitor(make_value, model_value):
    if (make_value is None) and (model_value is None):
        data_p = purchases.copy()
        data_c = competitors.copy()
        # Only provide intersection of data
        data_c = data_c[data_c['car_make'].isin(data_p['car_make'].unique())]

        # Plot competitor data
        fig = px.box(data_c, x='car_make', y='purchase_price')

        # I would like to add a red line here for each X value that
        # corresponds with the y value of the average purchase price
        # for the user of the dashboard (from purchases csv) so that
        # they can see where they fall compared to competitors
        # (insight: if the price is extremely high compared to 
        # competitors, does their value add back it? if low, is there
        # room for more revenue capture?)
        # Running out of time to add...but wanted to include note.
        
    elif (make_value is not None) and (model_value is None):
        data_p = purchases[purchases['car_make'] == make_value]
        data_c = competitors[competitors['car_make'] == make_value]
        # Only provide intersection of data
        data_c = data_c[data_c['car_model'].isin(data_p['car_model'].unique())]

        fig = px.box(data_c, x='car_model', y='purchase_price')

    else:
        data_p = competitors[(competitors['car_make'] == make_value) & (competitors['car_model'] == model_value)]
        data_c = competitors[(competitors['car_make'] == make_value) & (competitors['car_model'] == model_value)]
        # Only provide intersection of data
        data_c = data_c[data_c['car_model'].isin(data_p['car_model'].unique())]

        fig = px.box(data_c, x='car_model', y='purchase_price')

    return fig


if __name__ == '__main__':
    app.run(debug=False)
