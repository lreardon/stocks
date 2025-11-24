from collections import Counter
import numpy as np
from typing import Sequence, Any

def entropy(sequence: Sequence[Any]) -> float:
    """Calculate Shannon entropy of a sequence."""
    if len(sequence) == 0:
        return 0.0
    
    # Count symbol frequencies
    counts: Counter[Any] = Counter(sequence)
    total = len(sequence)
    
    # Calculate Shannon entropy: -sum(p * log2(p))
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * np.log2(p)
    
    return entropy