from tohlcv import TOHLCV
from typing import Optional

class Trade:
	profit_trigger: float
	loss_trigger: float
	entry: Optional[TOHLCV]
	exit: Optional[TOHLCV]
	
	def __init__(self, profit_trigger: float, loss_trigger: float):
		self.profit_trigger = profit_trigger
		self.loss_trigger = loss_trigger

	def exit_trade(self, exit: TOHLCV):
		self.exit = exit

	def enter_trade(self, entry: TOHLCV):
		self.entry = entry

	@property
	def exited(self) -> bool:
		return self.exit is not None

	@property
	def loss_trigger_price(self) -> float | None:
		if (self.entry_price is None):
			return None
		return self.loss_trigger * self.entry_price
			
	@property
	def profit_trigger_price(self) -> float | None:
		if (self.entry_price is None):
			return None
		return self.profit_trigger * self.entry_price

	def process_current_price(self, current: TOHLCV):
		current_price = current.close_price
		if (
			current_price >= self.profit_trigger_price or
			current_price <= self.loss_trigger_price
		):
			self.exit_trade(current)
	
	def __str__(self):
			if not self.exited:
				return 'Trade ongoing'

			if (self.exit_price is None or self.entry_price is None or self.trade_percent_change is None or self.trade_duration_in_minutes is None):
				raise ValueError('Exited trades should have entry and exit prices')
			
			s = 'Trade\n'
			s += 'Duration: '+ str(self.exit.timestamp - self.entry.timestamp)+'\n'
			s += ('PROFIT' if self.exit_price > self.entry_price else 'LOSS')+'\n'
			s += str(self.entry_price)+' --> '+str(self.exit_price)+'\n'
			s += 'Percent change per hour: ' + str(self.trade_percent_change / (self.trade_duration_in_minutes / 60))
			return s

	@property
	def exit_price(self) -> float | None:
		if self.exit is None: return None
		return self.exit.close_price
	
	@property
	def entry_price(self) -> float | None:
		if self.entry is None:
			return None
		return self.entry.close_price
	
	@property
	def trade_percent_change(self) -> float | None:
		if not self.exited: return None
		if self.exit_price is None or self.entry_price is None:
			raise ValueError('Exited trades should have entry and exit prices')
		
		return 100*(self.exit_price - self.entry_price)/self.entry_price

	
	@property
	def trade_duration_in_minutes(self)	-> float | None:
		if not self.exited: return None
		time_delta = self.exit.timestamp - self.entry.timestamp
		return time_delta.total_seconds() / 60