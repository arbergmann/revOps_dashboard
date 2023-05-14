import os
import pandas as pd
import numpy as np

def load_data():
    # Import data
    pth = os.getcwd()
    purchases = pd.read_csv(pth+"/assets/purchases.csv", index_col='id')
    opportunities = pd.read_csv(pth+"/assets/opportunities.csv", index_col='id')
    competitors = pd.read_csv(pth+"/assets/competitor_data.csv", index_col='id')

    # Data cleaning
    purchases['opportunity_created'] = pd.to_datetime(purchases['opportunity_created'])
    purchases['date_purchased'] = pd.to_datetime(purchases['date_purchased'])
    purchases['pct_financed'] = np.where(purchases['financed'] == False, 0, purchases['pct_financed']) # Formatting data where Mockaroo would not cooperate

    opportunities['opportunity_created'] = pd.to_datetime(opportunities['opportunity_created'])
    competitors['date_purchased'] = pd.to_datetime(competitors['date_purchased'])

    return purchases, opportunities, competitors