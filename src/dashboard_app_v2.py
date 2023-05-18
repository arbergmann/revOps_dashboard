#%%
from dash import Dash, html, dcc, Input, Output, State, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
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

# Spin up app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

#4285F4
# Define app layout
app.layout = html.Div([
    html.Div([
        # Title Banner
        html.H1("RevOps Dashboard for Used Car Sales", className="app_header__title", style={"textAlign":"center"}),
        html.P("This app acts as a revenue ops dashboard for a fictional used car dealership, leveraging fictional data.", className="app__header_title--grey", style={"textAlign":"center"})
    ], className="app_header_desc"),
    html.Div([
        html.A(html.Button("SOURCE CODE", className="link-button", style={"textAlign":"right"}), href="https://github.com/arbergmann/revOps_dashboard"),
        # html.A(html.Img(src=app.get_asset_url("assets/clipart2385495.png"), className="app__menu__img", style={"textAlign":"right"})),
    ], className="app__header__logo"),
    ## Car make filter
    html.Hr(),
    html.Div([
        html.Div([
        dcc.Dropdown(id='make_dd', 
                    clearable=True, 
                    value=None,
                    placeholder='Filter by Car Make (Optional)',
                    options=[{'label' : i, "value" : i} for i in sorted(purchases['car_make'].unique())]),
        ], className="two columns"), 
        html.Div([
        dcc.Dropdown(id='model_dd', 
                    clearable=True, 
                    value=None,
                    placeholder='Filter by Car Model (Optional)'),
        ], className="two columns")], 
        style=dict(display='flex'), className="row"),
    html.Br(),
    
    # Tabs
    html.Div([
        dcc.Tabs(id='tabs-div', value='tab-1', children=[
            dcc.Tab(label='Sales Metrics', value='tab-1'),
            dcc.Tab(label='Sales Lifecycle', value='tab-2'),
            dcc.Tab(label='Financial Analysis', value='tab-3'),
            dcc.Tab(label='Competitor Analysis', value='tab-4')
        ]),
    html.Div(id='tabs-content')
    ])
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

# Callback for tabs
@app.callback(Output('tabs-content', 'children'), 
              Input('tabs-div', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H2("Overall Statistics", style={"textAlign" : "center"}),
            html.Div(id='overall-stats', children=[], className="row"),
            html.Hr(),
            html.H2("Sales Metrics", style={"textAlign" : "center"}),
            html.Div(id='sales-div', children=[])
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.Div(id='sales-lifecycle-div', children=[])
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.Div(id='financial-analysis-div', children=[])
        ])

    elif tab == 'tab-4':
        return html.Div([
            html.Div(id='competitor-analysis-div', children=[])
        ])

# Callback for basic overall statistics
@app.callback(Output('overall-stats','children'),
              Input('make_dd', 'value'))
def overall_stats(make_dd):
    return [html.Div([
                html.Div([
                    dcc.Markdown("""
                                 ### Total Purchases (6m)
                                 ###### {}
                                 """.format(str(chart_functions.purchase_count(purchases))),
                                 style={"textAlign" : "center", "borderWidth": "3px",
                                        "borderStyle": "solid","borderColor": "#4287F5", 
                                        "backgroundColor": "#EEEEEE", "padding": "0.5%",})],
                                 className="three columns"),
                html.Div([
                    dcc.Markdown("""
                                 ### Total Opportunities (6m)
                                 ###### {}
                                 """.format(str(chart_functions.opportunity_count(purchases, opportunities))), 
                                 style={"textAlign" : "center", "borderWidth": "3px",
                                        "borderStyle": "solid","borderColor": "#4287F5", 
                                        "backgroundColor": "#EEEEEE", "padding": "0.5%",})],
                                 className="three columns"),
                html.Div([
                    dcc.Markdown("""
                                 ### Total Win Rate
                                 ###### {:.2%}
                                 """.format(chart_functions.win_rate(purchases, opportunities)),
                                 style={"textAlign" : "center", "borderWidth": "3px",
                                        "borderStyle": "solid","borderColor": "#4287F5", 
                                        "backgroundColor": "#EEEEEE", "padding": "0.5%",})],
                                 className="three columns"),
                html.Div([
                    dcc.Markdown("""
                                 ### Sales Cycle Length
                                 ###### {} Days
                                 """.format(chart_functions.avg_sales_cycle(purchases)),
                                 style={"textAlign" : "center", "borderWidth": "3px",
                                        "borderStyle": "solid","borderColor": "#4287F5", 
                                        "backgroundColor": "#EEEEEE", "padding": "0.5%",})],
                                 className="three columns")
                ], className="row")
            ]


############################
### Sales Metrics Charts ###
############################
@app.callback(Output('sales-div','children'),
              Input('make_dd', 'value'),
              Input('model_dd', 'value'))
def sales_metrics_charts(make_value, model_value):

    ## Data filtering based on filtering inputs
    if ((make_value is None) and (model_value is None)) | ((make_value is None) and (model_value is not None)):
        data = purchases.copy()
        pth = ['car_make', 'car_model']
    elif (make_value is None) and (model_value is not None):
        data = purchases.copy()
        pth = ['car_make', 'car_model']
    elif (make_value is not None) and (model_value is None):
        data = purchases[purchases['car_make'] == make_value]
        pth = ['car_model', 'car_year']
    else:
        data = purchases[(purchases['car_make'] == make_value) & (purchases['car_model'] == model_value)]
        pth = ['car_model', 'car_year']


    ## Histogram
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



    ## YoY Sales
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

    # arima_predictions = chart_functions.arima_predictions(data, ci=0.10)
    # # Add a row with most recent data so that the charts connect, converging at point
    # last_mth_row = pd.DataFrame({'month_delta' : -1, 'predicted_sales' : ttm_all['ttm'].tail(1), 
    #                              'prediction_lower_bound' : ttm_all['ttm'].tail(1),
    #                              'prediction_upper_bound' : ttm_all['ttm'].tail(1)})
    # arima_predictions = pd.concat([last_mth_row, arima_predictions], axis=0)

    fig_yoy = go.Figure()
    # Add historical "#224680"
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

    ## Sunburst breakdown
    # colorscale = [
    #     [0, 'rgb(0,0,0)'],
    #     [0.5, 'rgb(66,135,245)'],
    #     [1, 'rgb(34,70,128)']
    # ]
    
    fig_sburst = px.sunburst(data, 
                      path=pth, 
                      values='purchase_price', 
                      color_continuous_scale=['#FFFFFF', '#4285F4', '#224680'], # Not working...?
                      )
    fig_sburst.update_layout(title_text='Sales Breakdown by Type (%)', title_x = 0.5)

    ## Tables
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

    # fig_table_sales = dash_table.DataTable(top_5_sales.to_dict('records'), [{"name": i, "id": i} for i in top_5_sales.columns], id='sales5-tbl')
    # fig_table_count = dash_table.DataTable(top_5_count.to_dict('records'), [{"name": i, "id": i} for i in top_5_count.columns], id='count5-tbl')

    ## Return all charts back to tab
    return [html.Div([dcc.Graph(figure=fig_yoy)],className="row"),
            html.Hr(),
            html.Div([html.Div([dcc.Graph(figure=fig_hist)], className='eleven columns')], className="row"),
            html.Hr(),
            html.Div([
                html.Div([dcc.Graph(figure=fig_sburst)], className="seven columns"),
                html.Div([
                    html.H4("Highest Sales by Count and Dollar Value", style={"textAlign":"center"}),
                    html.Div([dash_table.DataTable(top_5_sales.to_dict('records'), [{"name": i, "id": i} for i in top_5_sales.columns], id='sales5-tbl')], className='two columns'),
                    html.Div([dash_table.DataTable(top_5_count.to_dict('records'), [{"name": i, "id": i} for i in top_5_count.columns], id='count5-tbl')], className='two columns')
                ])
    ], className="row"),
    ]



#################################
### Financial Analysis Charts ###
#################################
# @app.callback(Output('slider-output', 'children'),
#               Input('make_dd', 'value'))
# def sankey_slider(make_dd):
#     fin = financials.reset_index()
#     fin.rename(columns={'index':'income_stmt_line'}, inplace=True)
#     fin = pd.melt(fin, id_vars=['income_stmt_line'], var_name='fiscal_quarter')

#     # Build slider marks
#     slider_marks = {}
#     slider_options = sorted(fin['fiscal_quarter'].unique())
#     for fq in slider_options:
#         slider_marks[slider_options.index(fq)] = fq

#     return [html.Div([
#                 html.P("Year"),
#                 dcc.Slider(id='slider', min=0, max=len(slider_marks)-1, value=len(slider_marks)-1, marks=slider_marks)
#             ])]

@app.callback(Output('financial-analysis-div','children'),
              Input('make_dd', 'value'))
def financial_analysis_charts(slider_output):
    global financials

    ## Financial Statements
    qoq_pct_change = financials.iloc[:,-1] / financials.iloc[:,-2] - 1
    qoq_pct_change = qoq_pct_change.apply(lambda x: "{0:.2f}%".format(x*100))
    qoq_pct_change.name = 'Q/Q Chg'

    yoy_pct_change = financials.iloc[:,-1] / financials.iloc[:,-5] - 1
    yoy_pct_change = yoy_pct_change.apply(lambda x: "{0:.2f}%".format(x*100))
    yoy_pct_change.name = 'Y/Y Chg'

    financial_statements = pd.concat([financials.iloc[:,-1].apply(lambda x: f"${x/1000:,.0f}"), 
                                    financials.iloc[:,-2].apply(lambda x: f"${x/1000:,.0f}"), 
                                    qoq_pct_change, 
                                    financials.iloc[:,-5].apply(lambda x: f"${x/1000:,.0f}"), 
                                    yoy_pct_change], axis=1)
    financial_statements.columns = [x.upper().replace('_',' ') for x in list(financial_statements.columns)]
    financial_statements.index.rename('Line Item', inplace=True)
    financial_statements.reset_index(inplace=True)
    financial_statements['Line Item'] = financial_statements['Line Item'].apply(lambda x: x.upper().replace('_',' '))

    ## Sankey Chart
    fin = financials['2023_q1'].values

    fig_sankey = go.Figure(data=[go.Sankey(
                                node=dict(
                                    pad=15,
                                    thickness=20,
                                    line=dict(color="black", width=0.5),
                                    label=["Car Sales Revenue", "Rental Revenue", "Financing Revenue", "Gross Revenue", "Cost of Goods Sold", 
                                        "Gross Margin", "Operating Expenses", "Operating Income", "Tax Expense", "Net Income"],
                                    color="#4285F4"
                                ),
                                link=dict(
                                    source = [0,1,2,3,3,5,5,7,7],
                                    target = [3,3,3,4,5,6,7,8,9],
                                    value = [fin[0], fin[1], fin[2], fin[4], fin[5], fin[6], fin[7], fin[8], fin[9]]
                                )
                            )])
    fig_sankey.update_layout(title=dict(text="Income Statement Breakdown"), title_x = 0.5)

    ## Revenue Funnel
    fin = financials.T.tail(5)[['car_sales_revenues', 'rental_revenues', 'financing_revenues']]
    fin = fin.iloc[::-1]
    stages = list(fin.index)

    fig_funnel = go.Figure()

    fig_funnel.add_trace(go.Funnel(name='Car Sales Rev', y=stages, x=fin['car_sales_revenues'], marker={"color": "#4285F4"}, textinfo='value'))
    fig_funnel.add_trace(go.Funnel(name='Rental Rev', y=stages, x=fin['rental_revenues'], marker={"color": "#3469BF"}, textinfo='value'))
    fig_funnel.add_trace(go.Funnel(name='Financing Rev', y=stages, x=fin['financing_revenues'], marker={"color": "#224680"}, textinfo='value'))
    fig_funnel.update_layout(title=dict(text="Year-Over-Year Revenue Mix"), title_x = 0.5)

    return [html.Div([
                html.Div([
                    html.H4("Income Statements", style={"textAlign":"center"}),
                    # html.Hr(),
                    html.Div([dash_table.DataTable(financial_statements.to_dict('records'), [{"name": i, "id": i} for i in financial_statements.columns], id='financials-tbl')]),
                ], className="six columns"),
                html.Div([
                    html.Div([
                        html.Div([dcc.Graph(figure=fig_sankey)], className='row'), 
                    ], className="six columns"),
                ], className="row"),
                html.Hr(),
                html.Div([dcc.Graph(figure=fig_funnel)], className='row'),
    ])]

# html.Div([dash_table.DataTable(financial_statements.to_dict('records'), [{"name": i, "id": i} for i in financial_statements.columns], id='financials-tbl')], className='two columns'),

##################################
### Competitor Analysis Charts ###
##################################
@app.callback(Output('competitor-analysis-div','children'),
              Input('make_dd', 'value'),
              Input('model_dd', 'value'))
def competitor_analysis_charts(make_value, model_value):
    global purchases, competitors

    ## Data filtering based on inputs
    if ((make_value is None) and (model_value is None)) | ((make_value is None) and (model_value is not None)):
        data_p = purchases.copy()
        data_c = competitors.copy()
        # Only provide intersection of data
        # data_c = data_c[data_c['car_make'].isin(data_p['car_make'].unique())]
        intersection = list(set(data_p['car_make']) & set(data_c['car_make']))
        data_p = data_p[(data_p['car_make'].isin(intersection))]
        data_c = data_c[(data_c['car_make'].isin(intersection))]
    # If make selected, but not model
    elif (make_value is not None) and (model_value is None):
        data_p = purchases.copy()
        data_c = competitors.copy()
        data_p = data_p[data_p['car_make'] == make_value]
        # data_c = data_c[data_c['car_model'].isin(data_p['car_model'].unique())]
        # Only provide intersection of data, what can be seen in purchase data
        intersection = list(set(data_p['car_model']) & set(data_c['car_model']))
        data_p = data_p[(data_p['car_make'] == make_value) & (data_p['car_model'].isin(intersection))]
        data_c = data_c[(data_c['car_make'] == make_value) & (data_c['car_model'].isin(intersection))]
    # If make & model selected
    else:
        data_p = purchases.copy()
        data_c = competitors.copy()
        data_p = data_p[(data_p['car_make'] == make_value) & (data_p['car_model'] == model_value)]
        # Only provide intersection of data, what can be seen in purchase data
        intersection = list(set(data_p['car_model']) & set(data_c['car_model']))
        data_p = data_p[(data_p['car_make'] == make_value) & (data_p['car_model'].isin(intersection))]
        data_c = data_c[(data_c['car_make'] == make_value) & (data_c['car_model'].isin(intersection))]

    
    ## If no competitor data for provided make/model, return error message
    if (model_value is not None) and ((len(intersection) == 0) or (model_value not in intersection)):
        return [html.Div([
                    html.Div([dcc.Markdown(f"""
                    No competitor data available for combination
                    Make: {make_value}
                    Model: {model_value}
                    """)
                    ], className="row"),
                ])]

    else:
        ## Competitor Price Box Plots
        if ((make_value is None) and (model_value is None)) | ((make_value is None) and (model_value is not None)):

            fig_boxes = px.box(data_c, x='car_make', y='purchase_price', title='Price Comparison by Make',
                               color_discrete_sequence=["#4287F5"], labels={'car_make':'Car Make'})
            fig_boxes.update_xaxes(categoryorder='category ascending')

            company_avgs = data_p.groupby('car_make')['purchase_price'].mean()
            x2 = company_avgs.index
            company_avgs = company_avgs.values

            fig_boxes.layout.xaxis2 = go.layout.XAxis(overlaying='x', range=[0,len(x2)], showticklabels=False)

            for i in range(len(x2)):
                bargap = 0.1
                x = [i, i+1]
                y = [company_avgs[i], company_avgs[i]]
                scatt = fig_boxes.add_scatter(x=x, y=y, mode='lines', xaxis='x2', 
                                              showlegend=False, line={'color':'#993729', 'width':2})

            fig_boxes.update_layout(title_text='Price Comparison by Model', title_x = 0.5, 
                                    xaxis_title='Car Model', yaxis_title='Average Price', showlegend=False)

        else:
            fig_boxes = px.box(data_c, x='car_model', y='purchase_price', color_discrete_sequence=["#4287F5"], )
            fig_boxes.update_xaxes(categoryorder='category ascending')

            company_avgs = data_p.groupby('car_model')['purchase_price'].mean()
            x2 = company_avgs.index
            company_avgs = company_avgs.values

            fig_boxes.layout.xaxis2 = go.layout.XAxis(overlaying='x', range=[0,len(x2)], showticklabels=False)

            for i in range(len(x2)):
                bargap = 0.1

                x = [i, i+1]
                y = [company_avgs[i], company_avgs[i]]
                scatt = fig_boxes.add_scatter(x=x, y=y, mode='lines', xaxis='x2', 
                                              showlegend=False, line={'color':'#993729', 'width':2})
            
            fig_boxes.update_layout(title_text='Price Comparison by Make', title_x = 0.5, 
                                    xaxis_title='Car Make', yaxis_title='Average Price', showlegend=False)


        # Top opportunities for pricing increases
        if make_value is None:
            competitor_meds = pd.DataFrame(competitors.groupby('car_make')['purchase_price'].median()).rename(columns={'purchase_price':'Competitor Median'})
            purchase_avgs = pd.DataFrame(purchases.groupby(['car_make']).agg({'purchase_price' : [np.mean, 'count']}).droplevel(axis=1, level=0)).rename(columns={'mean': 'Average Price', 'count':'Count'})

        else:
            competitor_meds = pd.DataFrame(competitors.groupby('car_model')['purchase_price'].median()).rename(columns={'purchase_price':'Competitor Median'})
            purchase_avgs = pd.DataFrame(purchases.groupby(['car_model']).agg({'purchase_price' : [np.mean, 'count']}).droplevel(axis=1, level=0)).rename(columns={'mean': 'Average Price', 'count':'Count'})

        pricing_deltas = pd.concat([competitor_meds, purchase_avgs], axis=1, join='inner', ignore_index=False)
        pricing_deltas['pricing_delta'] = pricing_deltas['Average Price'] - pricing_deltas['Competitor Median']
        pricing_deltas['pricing_delta_pct'] = pricing_deltas['Average Price'] / pricing_deltas['Competitor Median'] - 1
        pricing_deltas['Opportunity Cost'] = pricing_deltas['pricing_delta'] * pricing_deltas['Count']
        pricing_deltas.sort_values('Opportunity Cost', ascending=True, inplace=True)
        pricing_deltas = pricing_deltas.rename(columns={'pricing_delta_pct' : 'Pricing Delta (%)', 'pricing_delta' : 'Pricing Delta ($)'}).head(10)

        for col in ['Average Price', 'Competitor Median', 'Pricing Delta ($)', 'Opportunity Cost']:
            pricing_deltas[col] = pricing_deltas[col].apply(lambda x: f"${x/1000:,.0f}k")
        pricing_deltas['Pricing Delta (%)'] = pricing_deltas['Pricing Delta (%)'].apply(lambda x: "{0:.2f}%".format(x*100))
        pricing_deltas.index.rename(' ', inplace=True)
        pricing_deltas.reset_index(inplace=True)
        

        ## Benchmarking
        c_tmp = competitors.groupby('car_tier')['purchase_price'].quantile([0.25, 0.5, 0.75, 0.9]).reset_index()
        c_tmp = c_tmp.rename(columns={'level_1' : 'percentile'})
        c_tmp = pd.pivot_table(c_tmp, values='purchase_price', index='car_tier', columns='percentile')
        c_tmp.columns = [str(x) for x in c_tmp.columns]
        
        p_tmp = purchases.groupby('car_tier')['purchase_price'].mean()

        x = c_tmp.index
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=x, y=c_tmp['0.25'], fill=None, mode='lines', line_color='#112340', name='25th Percentile'))
        fig_line.add_trace(go.Scatter(x=x, y=c_tmp['0.5'], fill='tonexty', mode='lines', line_color='#224680', name='Median'))
        fig_line.add_trace(go.Scatter(x=x, y=c_tmp['0.75'], fill='tonexty', mode='lines', line_color='#3469BF', name='75th Percentile'))
        fig_line.add_trace(go.Scatter(x=x, y=c_tmp['0.9'], fill='tonexty', mode='lines', line_color='#4287F5', name='90th Percentile'))
        fig_line.add_trace(go.Scatter(x=x, y=p_tmp.values, fill=None, mode='lines', name='Company Avg', line=dict(dash="dash", color='#993729', width=2)))
        fig_line.update_xaxes(title='Tier', tickangle=45)
        fig_line.update_yaxes(title='Average Sales Price')
        fig_line.update_layout(title_text="Product Benchmark Comparison by Tier", title_x = 0.5)

        ## Return all charts back to tab
        return [html.Div([
                    html.Div([dcc.Graph(figure=fig_boxes)], className="six columns"),
                    html.Div([
                        html.Br(),
                        html.H4("Highest Pricing Deltas and Opportunity Costs", style={"textAlign":"center"}),
                        html.Div([dash_table.DataTable(pricing_deltas.to_dict('records'), [{"name": i, "id": i} for i in pricing_deltas.columns], id='pricing-deltas-tbl')], className="five columns"),
                    ])
                ], className="row"),
                html.Hr(),
                html.H4("Benchmarking", style={"textAlign":"center"}),
                html.Div([
                    html.Div([dcc.Graph(figure=fig_line)]),
                ], className="row"),
        ]



if __name__ == '__main__':
    app.run(debug=True)

# %%
