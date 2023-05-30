# revOps_dashboard
a mock dashboard for revenue operations and pricing


<!-- ABOUT THE PROJECT -->
## About the Project

This is an sample dashboard that I put together for revenue operations and pricing. At this juncture, it leverages Dash/Plotly and is fairly rudamentary. I intend on expanding it out in the near future as time allows.

<b>How to interpret this project</b>
First and foremost, at the current stage, it is essentially a minimum viable product (well...more like pre-MVP). It is written for an audience that is primarily a pricing and monetization team that looks at pricing and value alignment, along with business strategy as it pertains to sales demand.

Initially, just as a passing thought and data availability, I decided to use car sales. When years were given as an option, I decided "used car sales" may be a better option, since it gave me more opportunities for breakdowns in charts down the lines. Eventually, I grew to regret this, as it ended up making some charts messy with all of the extensive breakdowns on already very individualized data. I tried to remedy this with batching additional data and restricting years to >=2010, and it helped a bit in certain cases.

Overall, this data is meant to be extremely "mock". Without extensive coding, there was no way to limit which cars got which prices, so it is entirely possible that a 2010 used Honda Accord gets listed as sold for $80k. This data is purely for visualization purposes and not to be looked into too hard as "logical."

The more I worked on this, the more I grew to think of it as product categories (make) and product offerings (models). Many of the principles here could be applied to something like retail or online services with multiple different product lines. If it helps to think of it more like that, perhaps that would be preferred.

<b>Data Sources</b><br>
<i>All data are from Mockaroo </i><br>
Data had to be batched in ~1000 row incremements due to Mockaroo limitations. This allowed for data to be manipulated over a few years so that no purchase dates should happen before an opportunity date.

- Purchase data
    - Purchases, primarily focused on price. Also contains opportunity data for opportunities that converted to clients.
- Opportunity data
    - Condensed version of `Purchase` data fields, with things like `car_make` turned to `car_make_interest`, as no purchase had been made. This results in significantly more nan values, but that ended up being somewhat irrelevant in the long run.
- Competitor data
    - Restricted to only company, make, model, pricing data. In real life, this could be scraped from various sources, or possibly sourced from a proprietary subscription data collation service like McKinsey's <i>PriceMetrix</i> for finance.
- Financial data
    - Basic financial income statements for the mock company.

All brainstorming ideas, mock-ups, and decision logs can be found the `decision_log.xlsx` document.

<b>Time Commitment Breakdown:</b><br>
- 1-2 hours brainstorming, building mock-ups
- 24-26 hours building actual code and troubleshooting
- 3-4 hours formatting and trying a few different layout options
- 3 hours code documentation, server testing

<br>
<br>

<!-- RUN THE CODE -->
## How to Run the Code

At this time, the dashboard is currently hosted at:

https://revops-dashboard.onrender.com

Given that Heroku is no longer free, I opted for Render. <b>Please Note: </b> Render's free servers are significantly slower than I would like. The first tab (`Sales Metrics`) is particularly slow to load/update filters, as it has a ML model running in the background to facilitate the prediction portion of the sales chart. Please give it sufficient time to load. If I find a better service for this, I will look into moving it.

To get a local copy up and running that may be faster, follow these steps:

1) Download the repository to your directory of choice.
2) Navigate to the `revops_dashboard` directory in the CLI.
3) Download the requirements with:
```sh
pip install -r requirements.txt
```
<b>Note: </b> You may see a note about incompatibility between two requirements. The app should still be able to render.<br>
4) Navigate to the `src` file using `cd src`
5) Run the following code:
```sh
python3 app.py
```
6) A localhost IP number will generate where you can access the development server to run the dashboard. Copy and pase this into a browser window.

<br>
<br>

<!-- CHALLENGES -->
## Challenges

<b>Data</b><br>
I was able to overcome some restrictions surrounding data pulls in Mockeroo, but due to the nature of the data I opted not to have a "closed" option for opportunities/accounts (purchases), which ultimately limited my lookback ability for things like client lifetime value.

The data was also extremely individualized, despite expanding from ~1000 samples for each non-financial subset to ~5000, I still only got minimal overlap to see significant, meaningful breakdowns. So, in certain areas this makes the charts seem a little bit messy, and perhaps difficult to get some initial insights from. That said, I was able to implement some controls to notate when smaller datasets affect the ability to generate charts (i.e. in the Sales Metrics tab).

<b>Code</b><br>
At this time, the code is fairly cumbersome. In the future, I would like to clean it up so that functions pull from the `chart_functions.py` file with optional parameters for filters/naming conventions that allow for cleaner code in the `app.py` file.


<br>
<br>

<!-- FUTURE CONSIDERATIONS -->
## Future Considerations


Given more time, I would make this code much more flexible and clean, possibly exploring opportunities for it to be more OOP-based, though I am not sure at this time that that is the appropriate decision. A the time of initial writing, I focused on getting something up and running in the time I had left, but that meant sometimes making sacrifices in approach, dynamic coding, and layout. For example, the calculations of the overall statistics assume all data is clean and consistent. In reality, this will not always be the case. I would have liked to include unit tests to check for the following:
- Checking date alignment (i.e. for things like `Opportunities` being created before `Purchases`)
- Checking data for cleanliness and reasonableness as it arrives (i.e. are values within reasonable ranges? Is any data "fat fingered" to have an extra order of magnitude?)
- Dashboard chart rendering

Some of the calculations were fairly rudimentary due to time constraints. I'd like to really dig into some of them more and flesh them out, check for contingencies that need to be incorporated from unclean or edge case data, etc.

I would like to expand out the chart offerings, as mentioned in the `Brainstorming` tab of the `decision_log.xlsx` file. Obviously, in reality, this would be far more dependent on client needs and actual data availability, as well. I'd also like to make the drop downs to have multiple options so comparisons are easier. Since there are so any individualized makes/models, if perhaps you could choose 2-3 instead of all or nothing, that would lend itself better to insights.

I felt the charts fell a little flat in terms of creativity and uniqueness, so I would like to expand on them more. Some ideas I would like to add/fix are:
- Win rate by make/model (to provide insight on where to focus sales efforts based on success, can cross-reference with inventories, most sold, etc.)
- Inventory counts and expenditure data/related charts/overlays on current charts (to see where inventories would need to be reduced/expanded, where price cuts may need to be made to move lower-demand products, etc.)
- More granularity on the `Financial Analysis` tab to uncover where margins are compressing in certain products, and where leeway on pricing vs demand may be available.
- Sales predictions outputs (to see where efforts on pricing should be focused, based on predictions)
- Customer acquisition markdown is just a mess... layout issues, not formatting color properly, not returning the correct string values, etc.
- Opportunities that do not turn to sales (to see where a product may be prohibitively expensive and pricing people out)
- Customer CLV/Churn based on product (to see which products are reducing retention)
- Willingness-to-Pay inclusion (this one is more of a "wish list" as I am not sure what the dataset would look like for this particular example, but would be cool to see how the current pricing falls compared to where customers are willing to pay...would work better on more retail/subscription services, I would imagine.)

I'd also like to improve layout and formatting. This feels sterile and blah in the current state. Most of the tables are in their default format, and I'd lke to add some more formatting to clarify important areas, especially in the financial analysis page with the Income Statements. I'd also like to add dropdown tabs that act as information on the dashboard page to help clarify what someone is looking at.

I also really just want to clean up the code a bit. It's not pretty, and could certainly be made more precise.
