#%%
from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import pandas as pd
import numpy as np
import sys, os
import chart_functions
import tools

#%%
# Import data
purchases, opportunities, competitors = tools.load_data()
car_make_set = set(purchases['car_make'].unique()).union(set(opportunities['car_make_interest'].unique()))
car_model_set = set(purchases['car_model'].unique()).union(set(opportunities['car_model_interest'].unique()))
# purchases

#%%

chart_functions.opportunity_count(purchases, opportunities)


# %%
# Spin up app
stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=stylesheet)

app.layout = html.Div([
    html.H1("RevOps Dashboard for Used Car Sales", style={"textAlign":"center"}),
    html.Hr(),
    html.P("Filter by car make (Optional): "),
    html.Div(html.Div([
        dcc.Dropdown(id='car_make_dropdown', 
                     clearable=True, 
                     options=[{'label' : i, 'value': i} for i in car_make_set],
                    placeholder="Car Make")
        ], className="three columns"), className="row"),

    html.P("Filter by car model (Optional): "),
    html.Div(html.Div([
        dcc.Dropdown(id='car_model_dropdown', 
                     clearable=True, 
                     options=[{'label' : i, 'value': i} for i in car_model_set],
                     placeholder='Car Model'),
        ], className="three columns"), className="row"),
    html.Div(id='output-div', children=[])
]) 

@app.callback([
    Output("car_model_dropdown", "options"),
    Output("car_model_dropdown", "value"),
    Input("car_make_dropdown", "value")
])
def update_dropdown_options(value):
    global df
    return[{'label' : i, 'value' : i} for i in purchases[purchases.car_make==value].car_model.unique()], None


@app.callback(Output(component_id='output-div', component_property='children'), 
              Input(component_id='car_make_type', component_property='value'),
              Input(component_id='car_model_type', component_property='value'),
              )
def generate_charts(car_make, car_model):

    global df

    # Filter data
    if (car_make is not None) and (car_model is not None):
        purch_filter = purchases[(purchases['car_make'] == car_make) & (purchases['car_model'] == car_model)]
        opp_filter = opportunities[(opportunities['car_make'] == car_make) & (opportunities['car_model'] == car_model)]

        purch_filter['month'] = purch_filter['date_purchased'].dt.month
        fig_hist = fig_hist = chart_functions.fig_histogram(purch_filter, x='month')

    elif (car_make is not None) and (car_model is None):
        purch_filter = purchases[(purchases['car_make'] == car_make)]
        opp_filter = opportunities[(opportunities['car_make'] == car_make)]

        fig_hist = fig_hist = chart_functions.fig_histogram(purch_filter, x='car_model')

    else:
        purch_filter = purchases.copy()
        opp_filter = opportunities.copy()

        fig_hist = fig_hist = chart_functions.fig_histogram(purch_filter, x='car_make')


    # Render Text boxes
    

    return [
        html.H2("Overall Statistics", style={"textAlign" : "center"}),
        html.Div([
            html.Div([dcc.Textarea(id='total_purchase', className='total_purchase',
                      value=chart_functions.purchase_count(purchases))]),
            html.Div([dcc.Textarea(id='total_opportunity', className='total_opportunity',
                      value=chart_functions.opportunity_count(purchases, opportunities))])
        ], className="row")
    ]


#%%
if __name__ == '__main__':
    app.run(debug=False)
# %%
