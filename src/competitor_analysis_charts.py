import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def competitor_box_plots(make_value, model_value, data_c, data_p):
    """ Box plots of company avg against competitor IQR, distribution breakdown by make/model
    Arguments:
    make_value (str) -- dropdown value of car make
    model_value (str) -- dropdown value of car model
    data_p (DataFrame) -- purchase data previously loaded in from csv
    data_c (DataFrame) -- competitor data previously loaded in from csv

    Returns:
    chart figure
    """
    if ((make_value is None) and (model_value is None)) | ((make_value is None) and (model_value is not None)):
        # If no make value is chosen, segment by make
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
        # If make value chosen, segment by model
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

    return fig_boxes


def pricing_deltas_list(competitor_meds, purchase_avgs):
    """ Table of highest differences from company average to competitor median.
    Arguments:
    competitor_meds (DataFrame) -- dataframe of competitor medians, by make/model
    purchase_avgs (DataFrame) -- dataframe of company averages, by make/model

    Returns:
    chart figure
    """
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

    return pricing_deltas


def benchmarking_chart(competitors, purchases):
    """ Benchmarking chart comparing company prices to competitor prices, by tiers
    Arguments:
    purchases (DataFrame) -- purchase data previously loaded in from csv, filtered by make/model
    competitors (DataFrame) -- competitor data previously loaded in from csv, filtered by make/model

    Returns:
    chart figure
    """
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

    return fig_line