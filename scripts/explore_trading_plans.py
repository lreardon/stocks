from trade import Trade
from trading_plan import TradingPlan
from tohlcv import TOHLCV
from trading_plan_tester import TradingPlanTester
import pandas as pd
import numpy as np

def report_trade(trade: Trade):
	print('*************************')
	print('\n')
	print(trade)
	print('\n')
	print('*************************')

def test_trading_plan(trading_plan: TradingPlan, training_df: pd.DataFrame):
	for index, row in training_df.iterrows():
		trade: Trade = trading_plan.create_trade()
		entry = TOHLCV(*row)
		trade.enter_trade(entry)
		jindex: int = int(index)
		while not trade.exited:
			jindex += 1
			jrow = training_df.iloc[jindex]
			current = TOHLCV(*jrow)
			trade.process_current_price(current)
			if trade.exited:
				report_trade(trade)
				print('\n\n')


if __name__ == "__main__":	
	training_df = pd.read_feather('spy_data_training.feather')

	# Define the ranges and steps for profit_trigger and loss_trigger
	profit_trigger_range = np.arange(1.01, 1.51, 0.01)
	loss_trigger_range = np.arange(0.5, 1.0, 0.01)

	# Create the 2D numpy array
	trigger_array = np.array(np.meshgrid(profit_trigger_range, loss_trigger_range)).T.reshape(-1, 2)

	for profit_trigger, loss_trigger in trigger_array:
		trading_plan = TradingPlan(profit_trigger, loss_trigger)
		tester = TradingPlanTester(trading_plan)
		tester.test_trading_plan(training_df)