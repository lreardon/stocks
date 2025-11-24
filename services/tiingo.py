import requests
from requests import Response
import os
from pathlib import Path
from datetime import date
from dateutil.relativedelta import relativedelta
import json


class Tiingo:
    API_TOKEN = '337dddf998c6495cb511f76aeef03e4973f7e0df'
    ENDPOINT = 'https://api.tiingo.com/'

    def __init__(self):
        pass

    def get_historical_particular(
            self,
            ticker: str,
            start_date: date,
            end_date: date,
        ):
        url: str = self.ENDPOINT + 'iex/' + ticker + '/prices'
        # Appears to limit to 10000 responses per request.
        response: Response = requests.get(
            url,
            params={
                'startDate': start_date.isoformat(),
                'endDate': end_date.isoformat(),
                'resampleFreq': '1min',
                'afterHours': 'false',
                'forceFill': 'true',
                'format': 'json',
                'columns': 'open,high,low,close,volume',
            },
            headers={
                'Authorization': 'Token ' + self.API_TOKEN,
                'Content-Type': 'application/json'
            },
        )
        response.raise_for_status()

        data = response.text

        cwd = Path.cwd()
        rel_path: str = 'data/'+ticker.lower()+'/tiingo/'+start_date.isoformat()+'--'+end_date.isoformat()+'.json'
        path: Path = cwd/rel_path
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            f.write(data)
    
    def get_historical_multimonth(
            self,
            ticker: str,
            months: int,
            merge: False,
        ):
        today = date.today()
        current_year = today.year
        current_month = today.month
        first_of_current_month = date(
            year=current_year,
            month=current_month,
            day=1,
        )

        self.get_historical_particular(
            ticker=ticker,
            start_date=first_of_current_month,
            end_date=today,
        )

        for num_months_back in range(months):
            end_date = first_of_current_month - relativedelta(months=num_months_back) - relativedelta(days=1)
            start_date = first_of_current_month - relativedelta(months=num_months_back + 1)

            self.get_historical_particular(
                ticker,
                start_date=start_date,
                end_date=end_date
            )

        if merge:
            self.merge_data(
                ticker=ticker
            )

    def merge_data(self, ticker: str):
        cwd = Path.cwd()
        relative_dir: str = 'data/'+ticker+'/tiingo'
        dir: Path = cwd/relative_dir
        filenames: list[str] = sorted([f for f in os.listdir(dir)
                                       if os.path.isfile(os.path.join(dir, f))
                                       and f.endswith('.json')
                                ])

        historical_file_name: str = 'historical.jsonl'
        historical_file_path: Path = dir/historical_file_name

        existing_dates = set()
        if historical_file_path.exists():
            with open(historical_file_path, 'r') as f:
                for line in f:
                    if line.strip():
                        datum = json.loads(line)
                        existing_dates.add(datum['date'])

        with open(historical_file_path, 'a') as f:
            for datafile_name in filenames:
                datafile_path = dir/datafile_name
                with open(datafile_path, 'r') as d:
                    data = json.load(d)
                    for datum in data:
                        date = datum['date']
                        if date not in existing_dates:
                            if existing_dates:
                                f.write('\n')
                            f.write(json.dumps(datum))
                            existing_dates.add(date)

      
t = Tiingo()
# t.merge_data(
#     ticker='SPY',
# )
t.get_historical_multimonth(
    ticker='QQQ',
    months=24,
    merge=True,
)