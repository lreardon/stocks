from trading_plan import TradingPlan
import pandas as pd
from trade import Trade
from tohlcv import TOHLCV

class TradingPlanTester:
	def __init__(self, trading_plan: TradingPlan):
		self.trading_plan = trading_plan
		
	
	def test_trading_plan(self, training_df: pd.DataFrame):
		for index, row in training_df.iterrows():
			trade: Trade = self.trading_plan.create_trade()
			entry = TOHLCV(*row)
			trade.enter_trade(entry)
			jindex = int(index)
			while not trade.exited:
				jindex += 1
				jrow = training_df.iloc[jindex]
				current = TOHLCV(*jrow)
				trade.process_current_price(current)
				if trade.exited:
					self.report_trade(trade)
					print('\n\n')

	def report_trade(self, trade: Trade):
		print('*************************')
		print('\n')
		print(trade)
		print('\n')
		print('*************************')