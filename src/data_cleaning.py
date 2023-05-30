#%%
import pandas as pd
import numpy as np
import os, sys
import random

"""
This is a single-use script for creating the overall datasets.

This includes collating Mockaroo datasets, generating financial dataset,
making some formatting edits to all datasets, and re-saving them in
the proper format to feed into the app.py file.
"""


path = os.path.dirname(os.getcwd()) + '/assets'

# Collate purchases
purchases = pd.DataFrame()
for file in [x for x in os.listdir(path+'/raw_purchases_data') if x.startswith('purchase')]:
    # f = os.path.join(path, file)
    df = pd.read_csv(path + '/raw_purchases_data/' + file, index_col='id')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    purchases = pd.concat([purchases,df], axis=0).reset_index(drop=True)


# Collate competitors
competitors = pd.DataFrame()
for file in [x for x in os.listdir(path+'/raw_competitor_data') if x.startswith('competitor')]:
    # f = os.path.join(path, file)
    df = pd.read_csv(path + '/raw_competitor_data/' + file, index_col='id')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    competitors = pd.concat([competitors,df], axis=0).reset_index(drop=True)

# Collate opportunitites
opportunities = pd.DataFrame()
for file in [x for x in os.listdir(path+'/raw_opportunities_data') if x.startswith('opportunities')]:
    # f = os.path.join(path, file)
    df = pd.read_csv(path + '/raw_opportunities_data/' + file, index_col='id')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    opportunities= pd.concat([opportunities,df], axis=0).reset_index(drop=True)


### Assign tiers
tiers = ['Budget', 'Economy', 'Off-Road', 'Sports', 'Luxury']
purchases['car_tier'] = random.choices(tiers, k=len(purchases))
competitors['car_tier'] = random.choices(tiers, k=len(competitors))

# Clean up financing in Opportunities/Purchases
random_pcts = [random.uniform(0, 0.95) for x in range(len(opportunities))]
opportunities['pct_financed'] = np.where(opportunities['financing_reqd'] == False, 0, random_pcts)
purchases['pct_financed'] = np.where(purchases['pct_financed'] == False, 0, purchases['pct_financed'])

# Clean up all car years - nothing less than 2010
random_yr = [random.randint(2010,2023) for x in range(5000)]
purchases['car_year'] = np.where(purchases['car_year'] >= 2010, purchases['car_year'], random_yr[:len(purchases)])
opportunities['car_year'] = np.where(opportunities['car_year_interest'] >= 2010, opportunities['car_year_interest'], random_yr[:len(opportunities)])
competitors['car_year'] = np.where(competitors['car_year'] >= 2010, competitors['car_year'], random_yr[:len(competitors)])

def generate_financials():
    """ This code generates the financials dataset.
    Returns:
    financials (DataFrame) -- dataframe of financials with quarters in columns, line items as rows/index
    """

    ### Generate financials
    years = [*range(2018, 2023, 1)]
    cols = []
    for y in years:
        for i in range(1,5):
            cols.append(str(y) + '_q' + str(i))
    cols.append('2023_q1')

    ## Calculate revenues
    cars_start = purchases[(purchases['date_purchased'] >= '2023-01-01') & (purchases['date_purchased'] < '2023-04-01')]['purchase_price'].sum()
    rental_services_start = random.randint(5000000,6000000)
    driving_services_start = random.randint(2000000,3000000)

    # Calculate car_sales
    car_revs = [cars_start]
    for x in range(len(cols)-1):
        new = car_revs[-1] * (1 + random.uniform(-0.025, 0.045))
        car_revs.append(round(new,2))
    car_revs = car_revs[::-1]

    # Calculate rental rev
    rental_revs = [rental_services_start]
    for x in range(len(cols)-1):
        new = rental_revs[-1] * (1 + random.uniform(-0.015, 0.035))
        rental_revs.append(round(new,2))
    rental_revs = rental_revs[::-1]

    # Calculate driving services rev
    financing_revs = [driving_services_start]
    for x in range(len(cols)-1):
        new = financing_revs[-1] * (1 + random.uniform(-0.015, 0.025))
        financing_revs.append(round(new,2))
    financing_revs = financing_revs[::-1]

    ## Calculate total revs
    total_revs = np.add(np.array(car_revs), np.array(rental_revs))
    total_revs = np.add(np.array(total_revs), np.array(financing_revs))

    ## Calculate COGS
    start = total_revs[-1] * 0.61
    cogs = [start]
    for x in range(len(cols)-1):
        new = cogs[-1] * (1 + random.uniform(-0.05, 0.05))
        cogs.append(round(new,2))
    cogs = cogs[::-1]

    ## Gross Margin
    gross_margin = np.subtract(np.array(total_revs), np.array(cogs))

    ## Operating Expenses
    start = gross_margin[-1] * 0.25
    opex = [start]
    for x in range(len(cols)-1):
        new = opex[-1] * (1 + random.uniform(-0.04, 0.04))
        opex.append(round(new,2))
    opex = opex[::-1]

    ## Marketing Expenses
    start = opex[-1] * 0.25
    marketing = [start]
    for x in range(len(cols)-1):
        new = marketing[-1] * (1 + random.uniform(-0.1, 0.1))
        marketing.append(round(new,2))
    marketing = marketing[::-1]

    ## Other Op-ex Expenses
    other_opex = np.subtract(np.array(opex), np.array(marketing))

    ## Operating Income
    op_income = np.subtract(np.array(gross_margin), np.array(opex))

    ## Tax Expense
    tx_ex = []
    for x in range(len(cols)):
        new = opex[x] * (1 + random.uniform(0.08, 0.18))
        tx_ex.append(round(new,2))
    tx_ex = tx_ex[::-1]

    ## Net Income
    net_income = np.subtract(np.array(op_income), np.array(tx_ex))

    data = {'car_sales_revenues' : car_revs,
            'rental_revenues' : rental_revs,
            'financing_revenues' : financing_revs,
            'total_revenue' : total_revs,
            'cost_goods_sold' : cogs,
            'gross_margin' : gross_margin,
            'marketing' : marketing,
            'other_opex' : other_opex,
            'operating_expenses' : opex,
            'operating_income' : op_income,
            'tax_expense' : tx_ex,
            'net_income' : net_income
            }

    financials = pd.DataFrame(data=data, index=cols).T
    return financials

financials = generate_financials()

purchases.to_csv(path + '/' + 'purchases.csv')
opportunities.to_csv(path + '/' + 'opportunities.csv')
competitors.to_csv(path + '/' + 'competitor_data.csv')
financials.to_csv(path + '/' + 'financials.csv')

# %%
