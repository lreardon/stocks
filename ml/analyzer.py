import pandas as pd
import datetime

class Analyzer():
	def __init__(self, ticker): # start_date, window_length, stop_loss, target
		ticker_data_path = f'../archive/Stocks/{ticker}.us.txt'
		self.df = pd.read_csv(ticker_data_path)

	def range(self, start_date, window_length_in_days): # stop_loss, target
		self.start_date = self.__date_string_to_datetime(start_date)
		end_date = self.start_date + datetime.timedelta(days=window_length_in_days)
		end_date_string = end_date.strftime('%Y-%m-%d')
		range = self.df[self.df['Date'].between(start_date, end_date_string)]
		return range
	
	def analyze(self, range, stop_loss, target):
		open = range.iloc[0]['Open']
		stop_loss_price = open * (1 - stop_loss)
		target_price = open * (1 + target)

		for row in range.iterrows():
			row = row[1]
			low = row['Low']
			if low < stop_loss_price:
				trade_duration = self.__date_string_to_datetime(row['Date']) - self.start_date
				print('stop loss reached in', trade_duration)
				return 'bad!'
			high = row['High']
			if high > target_price:
				trade_duration = self.__date_string_to_datetime(row['Date']) - self.start_date
				print('target reached in', trade_duration)
				return 'good!'
			
		print('trade was flat, waste of time')
		return 'inconclusive!'

	def __date_string_to_datetime(self, date_string):
		[start_year,start_month,start_day] = [int(d) for d in date_string.split('-')]
		return datetime.date(start_year, start_month, start_day)
	
a = Analyzer('aapl')