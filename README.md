# Stocks

Persisting my work for stock trading strategy development and analysis. Various sub-projects are grouped here, including some ML/AI-based projects and some classical strategies.

I have lots of additional locally, in folders `/data`, `/ml-datasets`, and `archive`. Those aren't uploaded here because they'd be too big for now.

## Following Along

If you're just found this, hi! The repo is large and a lot of it is old and not currently used. Current development is taking place in `/analysis/studies/study_three.ipynb` and related files. Thanks for looking and don't hesitate to contact me with questions or for collaboration.


## Fetching data

The way forward is to use tiingo to collect data. The tiingo data is collected from the API to `/data/{TICKER}/{{START_DATE--END_DATE}}.json` files and then collated into a `/data/{TICKER}/historical.jsonl` file. We're rate-limited to 50 API calls per day, so just add 2 more symbols every time.

Eventually, I'll come up with a nice script to efficiently get all the symbols "caught up" in a way that doesn't waste API calls. For now it's a luxury that coding alone in my free time cannot afford.