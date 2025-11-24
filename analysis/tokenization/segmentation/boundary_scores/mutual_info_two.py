from collections import Counter
import numpy as np
from typing import Sequence, Any

def mutual_info_two(left: Sequence[Any], right: Sequence[Any]):
    """Score boundary strength between segments."""
    # Simple approach: measure distribution difference
    left_dist = Counter(left)
    right_dist = Counter(right)
    
    # Normalize to probabilities
    left_probs = {k: v/len(left) for k, v in left_dist.items()}
    right_probs = {k: v/len(right) for k, v in right_dist.items()}
    
    # Jensen-Shannon divergence (symmetric)
    all_symbols = set(left) | set(right)
    js_div = 0.0
    
    for symbol in all_symbols:
        p = left_probs.get(symbol, 0)
        q = right_probs.get(symbol, 0)
        m = (p + q) / 2
        
        if p > 0 and m > 0:
            js_div += 0.5 * p * np.log2(p / m)
        if q > 0 and m > 0:
            js_div += 0.5 * q * np.log2(q / m)
    
    return js_div