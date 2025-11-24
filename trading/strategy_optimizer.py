import inspect
from typing import get_type_hints
import itertools

class StrategyOptimizer:
    def __init__(self,
        strategy: callable,
        param_range: dict,
        evaluator: callable = None,
    ):
        self.strategy = strategy
        self.param_range = param_range
        self.evaluator = evaluator
        self.best_params = None
        self.best_score = None

        self.param_combo_index = None

        self.results = []

        signature = inspect.signature(strategy)
        type_hints = get_type_hints(strategy)
        params = {}

        for name, param in signature.parameters.items():
            # Skip 'df' parameter (assuming first parameter is always DataFrame)
            if name == 'df':
                continue
                
            # Get type annotation if available
            param_type = type_hints.get(name, param.annotation)
            if param_type is inspect.Parameter.empty:
                param_type = None
            
            params[name] = {'type': param_type}

        assert len(params) == len(param_range)


    def optimize(self):
        param_names = list(self.param_range.keys())
        param_values = list(self.param_range.values())

        combinations = itertools.product(*param_values)

        for i, combo in enumerate(combinations):
            _param_combo_index = i
            params = dict(zip(param_names, combo))
            combo_result = self.strategy(**params)

            score = None
            if self.evaluator:
                score = self.evaluator(combo_result)
                if self.best_score is None or score > self.best_score:
                    self.best_score = score
                    self.best_params = params

            self.results.append((params, combo_result, score))