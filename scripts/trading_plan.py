from trade import Trade

class TradingPlan:
	def __init__(self, profit_trigger, loss_trigger):
		self.profit_trigger = profit_trigger
		self.loss_trigger = loss_trigger
		pass

	def create_trade(self) -> Trade:
		return Trade(self.profit_trigger, self.loss_trigger)
