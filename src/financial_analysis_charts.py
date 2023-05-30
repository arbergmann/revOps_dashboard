import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def income_statement(financials):
    """ Income statement table
    Arguments:
    financials (DataFrame) -- financial data previously loaded in from csv

    Returns:
    chart figure
    """
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

    return financial_statements

def sankey_chart(financials, quarter):
    """ Sankey chart of income statement breakdown
    Arguments:
    financials (DataFrame) -- financials data previously loaded in from csv
    quarter (str) -- quarter to post financials for

    Returns:
    chart figure
    """
    ## Sankey Chart
    fin = financials[quarter].values

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
                                    value = [fin[0], fin[1], fin[2], fin[4], fin[5], fin[8], fin[9], fin[10], fin[11]]
                                )
                            )])
    fig_sankey.update_layout(title=dict(text="Income Statement Breakdown"), title_x = 0.5)

    return fig_sankey

def revenue_funnel(financials):
    """ Revenue funnel showing change over time from different revenue streams
    Arguments:
    financials (DataFrame) -- purchase data previously loaded in from csv

    Returns:
    chart figure
    """
    fin = financials.T.tail(5)[['car_sales_revenues', 'rental_revenues', 'financing_revenues']]
    fin = fin.iloc[::-1]
    stages = list(fin.index)

    fig_funnel = go.Figure()

    fig_funnel.add_trace(go.Funnel(name='Car Sales Rev', y=stages, x=fin['car_sales_revenues'], marker={"color": "#4285F4"}, textinfo='value'))
    fig_funnel.add_trace(go.Funnel(name='Rental Rev', y=stages, x=fin['rental_revenues'], marker={"color": "#3469BF"}, textinfo='value'))
    fig_funnel.add_trace(go.Funnel(name='Financing Rev', y=stages, x=fin['financing_revenues'], marker={"color": "#224680"}, textinfo='value'))
    fig_funnel.update_layout(title=dict(text="Year-Over-Year Revenue Mix"), title_x = 0.5)

    return fig_funnel