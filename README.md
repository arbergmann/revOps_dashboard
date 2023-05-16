# revOps_dashboard
a mock dashboard for revenue operations and pricing


<!-- ABOUT THE PROJECT -->
## About the Project

This is an sample dashboard that I put together for revenue operations and pricing. At this juncture, it leverages Dash/Plotly and is fairly rudamentary. I intend on expanding it out in the near future as time allows.

<b>How to interpret this project</b>
First and foremost, at the current stage, it is essentially a minimum viable product (well...more like pre-MVP). It is written for an audience that is primarily a pricing and monetization team that looks at pricing and value alignment, along with business strategy.

Initially, just as a passing thought and data availability, I decided to use car sales. When years were given as an option, I decided "used car sales" may be a better option, since it gave me more opportunities for breakdowns in charts down the lines. Eventually, I grew to regret this, as it ended up making some charts messy with all of the extensive breakdowns on already very individualized data. I will likely remove this in future iterations of data generation.

Overall, this data is meant to be extremely "mock". Without extensive coding, there was no way to limit which cars got which prices, so it is entirely possible that a 1992 used Accord gets listed as sold for $80k. This data is purely for visualization purposes and not to be looked into too hard as logical.

The more I worked on this, the more I grew to think of it as product categories (make) and product offerings (models). Many of the principles here could be applied to something like retail or online services with multiple different product lines. If it helps to think of it more like that, perhaps that would be preferred until I can change out data to something that makes more sense.

<b>Data Sources</b>
<br>
<i>All data are from Mockaroo </i>
- Purchase data
- Opportunity data
- Competitor data

All brainstorming ideas, mock-ups, and decision logs can be found the `decision_log.xlsx` document.

<b>Time Commitment Breakdown:</b>
- 1-2 hours brainstorming, building mock-ups
- 3-4 hours building actual code
- 4-5 hours troubleshooting Dash-related rendering issues, refactoring
- 2 hours initial, code documentation

<br>
<br>
<!-- RUN THE CODE -->
## How to Run the Code

To get a local copy up and running, follow these steps:

1) Download the repository to your directory of choice.
2) Navigate to the `revops_dashboard` directory in the CLI.
3) This project leverages a conda environment. Create the environment using the following code:
```sh
conda env create -f environment.yml
```
4) Activate the conda environment using the following code:
```sh
conda activate revops
```
5) Navigate to the `src` file using `cd src`
6) Run the following code:
```sh
python3 dashboard_app.py
```
7) A localhost IP number will generate where you can access the development server to run the dashboard. Copy and pase this into a browser window.

<br>
<br>
<!-- CHALLENGES -->
## Challenges

<b>Data</b><br>
Some of the data-related challenges here were limitations with <i>Mockeroo</i>. As a free user, one is only allowed 1000 lines, so I had to diligently choose how to break that up. Upon my initial first pass, I chose to look at 6 months of purchase data, and 12 months of opportunity data (also included in the 6 months of purchase data). This allowed for some rudimentary calculations on sales cycle length and QoQ sales metrics, but limited my lookback ability for things like client lifetime value.

The data was also extremely individualized, and with 1000 samples, I still did not get enough overlap to see significant, meaningful breakdowns. For example, the car with the most sales only had 3 sales of that make/model (not even broken down by year). So, this makes the charts seem a little bit messy, and perhaps difficult to get some initial insights from. In fact, the QoQ sales chart trips the debugger when filters are used, simply because there are not enough observations of any given product on a breakdown. Given more time, I will look into how to make the data more repeatable so that the dashboard is more readable.

<b>Code</b><br>
Initially, the code was written fairly cleanly. I had a single callback for the filtering portion for the model (based on make selection), and a single callback to generate the charts. The chart codes were initially included in the `chart_functions.py` file and pulled into the callback function. This kept the code clean and neat and less than 150 lines.

The code was struggling to render for some reason. I tested previous codes that I had used similar setups for, and they were working fine (not an issue with deprecation, etc.), and the debug error messages were not offering any help in figuring out what part of the code was not passing through properly. For the sake of getting some sort of MVP working, I decided to just refactor the code a bit to include it in the `app.layout...` portion. This is not my favorite way to set these up.

I ended up using a conda environment, for no other reason but because I used it on my last project and it was fresh in my brain as the default. Otherwise, I typically use pip or venv.

<!-- FUTURE CONSIDERATIONS -->
## Future Considerations

Given more time, I would make this code much more flexible and clean. A the time of initial writing, I focused on getting something up and running in the time I had left, but that meant sometimes making sacrifices in approach and dynamic coding. For example, the calculations of the overall statistics assume all data is clean and consistent. In reality, this will not always be the case. Some of this could be helped with including unit tests, etc., but I simply ran out of time. I would also like to make the code more modular, leveraging the `chart_functions.py` file properly, as mentioned above.

Some of the calculations were fairly rudimentary due to time constraints. I'd like to really dig into some of them more and flesh them out, check for contingencies that need to be incorporated, etc.

I would like to expand out the chart offerings, as mentioned in the `Brainstorming` tab of the `decision_log.xlsx` file. I think I was limited on my data to begin with, and this ended up requiring me to make some concessions as time was running out. Obviously, in reality, this would be far more dependent on client needs, as well. I'd also like to make the drop downs to have multiple options. Since there are so any individualized makes/models, if perhaps you could choose 2-3 instead of all or nothing, that would lend itself better to insights.

I felt the charts fell a little flat in terms of creativity and uniqueness, so I would like to expand on them more. I would like to add some predictive modeling as well, as data science is my first priority domain.

I'd also like to improve layout and formatting. This feels sterile and blah in the current state, and the axes clearly need some TLC.

I also really just want to clean up the code a bit. It's not pretty, and I left some commented out areas for myself for some testing purposes in there, so I have them to work with later on.
