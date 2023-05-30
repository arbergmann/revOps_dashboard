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

# Import user libraries
import tools
import chart_functions
from sales_metrics_charts import yoy_sales_chart, sales_distribution_histogram, sunburst_chart, sales_metrics_tables
from sales_lifecycle_charts import ttm_sales_cycle_days, ttm_sales_cycle_strip, ttm_win_rate, customer_acq_cost
from financial_analysis_charts import income_statement, sankey_chart, revenue_funnel
from competitor_analysis_charts import competitor_box_plots, pricing_deltas_list, benchmarking_chart


# Load Data
purchases, opportunities, competitors, financials = tools.load_data()

# Spin up app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server


# Define app layout
app.layout = html.Div([
    html.Div([
        # Title Banner
        html.H1("RevOps Dashboard for Used Car Sales", className="app_header__title", style={"textAlign":"center"}),
        html.P("This app acts as a revenue ops dashboard for a fictional used car dealership, leveraging fictional data.", 
               className="app__header_title--grey", style={"textAlign":"center"})
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
    """ Generate Sales Metrics charts, all filtered by Make/Model
    In order:
    - Sales Histogram (count by make/model)
    - YoY sales + 3M forecast
    - Sunburst chart
    - Highest sales table breakdowns

    Arguments:
    make_value (string) -- Make filter output
    model_value (str) -- Model filter output

    Returns:
    charts (html.Div)
    """

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
    fig_hist = sales_distribution_histogram(make_value, model_value, data)


    ## YoY Sales
    fig_yoy = yoy_sales_chart(data)

    ## Sunburst breakdown
    fig_sburst = sunburst_chart(data, pth)

    ## Tables
    top_5_sales, top_5_count = sales_metrics_tables(make_value, data)

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



##############################
### Sales Lifecycle Charts ###
##############################
@app.callback(Output('sales-lifecycle-div','children'),
              Input('make_dd', 'value'),
              Input('model_dd', 'value'))
def sales_lifecycle_charts(make_value, model_value):
    """ Generate Sales Lifecycle charts, all filtered by Make/Model
    In order:
    - Sales cycle trend chart (Filtered - Model only)
    - Sales cycle by make/model (Filtered - Model only)
    - Win rate trend (Filtered - model only)
    - Win rate by make/model -- INCOMPLETE
    - Customer Acquisition chart (No filters)
    - Customer Acquisition markdowns (No filters, Not working)

    Customer acquisition does not break down due to lack of data at make/model level for marketing expenses.

    Arguments:
    make_value (string) -- Make filter output
    model_value (str) -- Model filter output

    Returns:
    charts (html.Div)
    """

    ## Data filtering based on filtering inputs
    if ((make_value is None) and (model_value is None)) | ((make_value is None) and (model_value is not None)):
        data_p = purchases.copy()
        data_o = opportunities.copy()
    elif (make_value is None) and (model_value is not None):
        data_p = purchases.copy()
        data_o = opportunities.copy()
    elif (make_value is not None) and (model_value is None):
        data_p = purchases[purchases['car_make'] == make_value]
        data_o = opportunities[opportunities['car_make_interest'] == make_value]
    else:
        data_p = purchases[(purchases['car_make'] == make_value) & (purchases['car_model'] == model_value)]
        data_o = opportunities[(opportunities['car_make_interest'] == make_value) & (opportunities['car_model_interest'] == model_value)]


    ## Trailing Twelve Months Sales Lifecycle Chart
    fig_ttm_cycle = ttm_sales_cycle_days(data_p)

    ## Trailing Twelve Months Sales Lifecycle by Model - Strip
    fig_strip_sales = ttm_sales_cycle_strip(make_value, data_p)

    ## Trailing Twelve Months Win Rate
    fig_ttm_winrt = ttm_win_rate(data_p, data_o)

    ## Customer Acquisition Trends
    fig_cust_cost, trend_yoy, trend_qoq, _, _ = customer_acq_cost(data_p, financials)


    return [html.Div([
                html.H2("Sales Cycle Time", style={"textAlign":"center"}),
                html.Div([dcc.Graph(figure=fig_ttm_cycle)], className="six columns"),
                html.Div([dcc.Graph(figure=fig_strip_sales)], className="five columns"),
            ], className="row"),
            html.Div([
                html.Hr(),
                html.H2("Win Rate", style={"textAlign":"center"}),
                html.Div([dcc.Graph(figure=fig_ttm_winrt)], className="six columns"),
                # html.Div([dcc.Graph(figure=fig_strip)], className="five columns"),
            ], className="row"),
            html.Div([
                html.Hr(),
                html.H2("Customer Acquisition Cost", style={"textAlign":"center"}),
                # Row of charts/printouts
                html.Div([
                    html.Div([dcc.Graph(figure=fig_cust_cost)], className="ten columns"),
                    html.Div([
                        # Print outs
                            html.Div([
                                dcc.Markdown("""The QoQ Trend is"""),
                                dcc.Markdown(f"""**{trend_qoq}**"""),
                                dcc.Markdown("""than last quarter"""),
                            ], style={"textAlign":"center", "verticalAlign" : 'center'}),
                            html.Br(),
                            html.Div([
                                dcc.Markdown("""The YoY Trend is"""),
                                dcc.Markdown(f"""**{trend_yoy}**"""),
                                dcc.Markdown("""than last quarter"""),
                            ], style={"textAlign":"center", "verticalAlign" : 'center'}),
                        ], className="two columns", style={"verticalAlign" : 'center'})
                    ], style={"verticalAlign" : 'center'}, className="row"),
                ])
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
    """ Generate Financial Analysis charts, NO RESPONSE TO FILTERS
    In order:
    - Financial Statements Table
    - Sankey Chart for Income Statement Breakdown
    - Year-over-Year Revenue Mix Breakdown

    Arguments:
    slider_output (string) -- Inoperable at this time

    Returns:
    charts (html.Div)
    """
    global financials

    ## Financial Statements
    financial_statements = income_statement(financials)

    ## Sankey Chart
    fig_sankey = sankey_chart(financials, '2023_q1')

    ## Revenue Funnel
    fig_funnel = revenue_funnel(financials)

    return [html.Div([
                html.Div([dcc.Markdown("**Note:** These charts do not change by filtering at this time.")], style={"textAlign":"center", "verticalAlign":"center"}),
                html.Div([
                    html.H4("Income Statements", style={"textAlign":"center"}),
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



##################################
### Competitor Analysis Charts ###
##################################
@app.callback(Output('competitor-analysis-div','children'),
              Input('make_dd', 'value'),
              Input('model_dd', 'value'))
def competitor_analysis_charts(make_value, model_value):
    """ Generate competitor analysis charts
    In order:
    - Price Comparison by Make (Filtered - Make/Model)
    - Pricing Deltas Table (Filtered - Model only)
    - Benchmarking (No Filter Responses at this time)

    Arguments:
    make_value (string) -- Make filter output
    model_value (str) -- Model filter output

    Returns:
    charts (html.Div)
    """
    global purchases, competitors

    ## Data filtering based on inputs
    if ((make_value is None) and (model_value is None)) | ((make_value is None) and (model_value is not None)):
        data_p = purchases.copy()
        data_c = competitors.copy()
        # Only provide intersection of data
        intersection = list(set(data_p['car_make']) & set(data_c['car_make']))
        data_p = data_p[(data_p['car_make'].isin(intersection))]
        data_c = data_c[(data_c['car_make'].isin(intersection))]
    # If make selected, but not model
    elif (make_value is not None) and (model_value is None):
        data_p = purchases.copy()
        data_c = competitors.copy()
        data_p = data_p[data_p['car_make'] == make_value]
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


    if (model_value is not None) and ((len(intersection) == 0) or (model_value not in intersection)):
         ## If no competitor data for provided make/model, return error message
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
        fig_boxes = competitor_box_plots(make_value, model_value, data_c, data_p)
    
        ## Top opportunities for pricing increases
        if make_value is None:
            competitor_meds = pd.DataFrame(competitors.groupby('car_make')['purchase_price'].median()).rename(columns={'purchase_price':'Competitor Median'})
            purchase_avgs = pd.DataFrame(purchases.groupby(['car_make']).agg({'purchase_price' : [np.mean, 'count']}).droplevel(axis=1, level=0)).rename(columns={'mean': 'Average Price', 'count':'Count'})

        else:
            competitor_meds = pd.DataFrame(competitors.groupby('car_model')['purchase_price'].median()).rename(columns={'purchase_price':'Competitor Median'})
            purchase_avgs = pd.DataFrame(purchases.groupby(['car_model']).agg({'purchase_price' : [np.mean, 'count']}).droplevel(axis=1, level=0)).rename(columns={'mean': 'Average Price', 'count':'Count'})

        # Pricing Deltas
        pricing_deltas = pricing_deltas_list(competitor_meds, purchase_avgs)

        ## Benchmarking
        fig_line = benchmarking_chart(competitors, purchases)

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
    app.run(debug=True, port=8060)

# %%
