import pandas as pd
from trading.strategies.strategy import Strategy
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from trading.strategies.enums.exit_type import ExitType


class StrategyEvaluator:
    df: pd.DataFrame

    def __init__(self, strategy: Strategy):
        self.strategy = strategy

    def load_data_from_path(self, path: Path):
        lines: bool = path.name.endswith('.jsonl')
        self.df: pd.DataFrame = pd.read_json(str(path), lines=lines)
    
    def load_historical_for_ticker(self, ticker: str):
        cwd = Path.cwd()
        datapath: Path = cwd/'data'/ticker/'tiingo/historical.jsonl'
        
        self.load_data_from_path(datapath)

    def apply_strategy(self):
        strategy_applied_df = self.strategy(self.df)
        self.df = strategy_applied_df
    
    def calculate_cumulative_returns(self):
        if 'profit_ratio' not in self.df.columns:
            raise ValueError("profit_ratio column not found. Run apply_strategy() first.")
        
        self.df['cumulative_return_ratio'] = self.df['profit_ratio'].cumprod()

    def plot_cumulative_returns(self):
        if 'cumulative_return_ratio' not in self.df.columns:
            self.calculate_cumulative_returns()
        
        plot_df = self.df.dropna(subset=['cumulative_return_ratio'])
        
        def assign_color(e):
            if e == ExitType.TAKE_PROFIT:
                return 'green' 
            if e == ExitType.STOP_LOSS:
                return 'red'
            if e == ExitType.TIMEOUT:
                return 'orange' 
            return '#ffffff00'
        
        colors = plot_df['exit_type'].apply(assign_color)


        plt.figure(figsize=(12, 6))
        plt.scatter(x=plot_df.index, y=plot_df['cumulative_return_ratio'], c=colors)
        plt.title('Cumulative Returns Over Time')
        plt.xlabel('Time')
        plt.ylabel('Cumulative Return Ratio')
        plt.yscale('log')
        plt.grid(True)
        plt.axhline(y=1, color='r', linestyle='--', alpha=0.7, label='Break-even')
        plt.legend()
        plt.show()
    
    def compute_sharpe_ratio(self):
        daily_returns = self.df.groupby('date')['profit_ratio'].prod() - 1
        sharpe_ratio = daily_returns.mean() / daily_returns.std()
        annualized_sharpe_ratio = sharpe_ratio * np.sqrt(252)
        return annualized_sharpe_ratio

