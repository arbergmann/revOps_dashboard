import os
import pandas as pd
import numpy as np

def load_data():
    """ Load the data into the code from csv files.
    Arguments:
    None

    Returns:
    purchases (DataFrame) -- a dataframe of purchase data
    opportunities (DataFrame) -- a dataframe of opportunity data
    competitors (DataFrame) -- a dataframe of competitor data
    """
    # Import data
    pth = os.path.dirname(os.getcwd()) # Go up one directory
    purchases = pd.read_csv(pth+"/assets/purchases.csv", index_col=0)
    opportunities = pd.read_csv(pth+"/assets/opportunities.csv", index_col=0)
    competitors = pd.read_csv(pth+"/assets/competitor_data.csv", index_col=0)
    financials = pd.read_csv(pth+"/assets/financials.csv", index_col=0)

    # Data cleaning
    purchases['opportunity_created'] = pd.to_datetime(purchases['opportunity_created'])
    purchases['date_purchased'] = pd.to_datetime(purchases['date_purchased'])
    purchases['pct_financed'] = np.where(purchases['financed'] == False, 0, purchases['pct_financed']) # Formatting data where Mockaroo would not cooperate
    purchases['month'] = purchases['date_purchased'].dt.month
    purchases['year'] = purchases['date_purchased'].dt.year

    opportunities['opportunity_created'] = pd.to_datetime(opportunities['opportunity_created'])
    opportunities['month'] = opportunities['opportunity_created'].dt.month
    opportunities['year'] = opportunities['opportunity_created'].dt.year
    
    
    competitors['date_purchased'] = pd.to_datetime(competitors['date_purchased'])
    competitors['month'] = competitors['date_purchased'].dt.month

    return purchases, opportunities, competitors, financials