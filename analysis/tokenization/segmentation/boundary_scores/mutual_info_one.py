from collections import Counter
from analysis.tokenization.segmentation.utils import entropy
import numpy as np
from typing import Sequence, Any

def mutual_info_one(left: Sequence[Any], right: Sequence[Any]) -> float:
    """Score the quality of a boundary between two segments."""
    # High score if segments are internally coherent but different from each other
    left_entropy = entropy(left)
    right_entropy = entropy(right)
    
    # Measure difference between segments
    left_dist = Counter(left)
    right_dist = Counter(right)
    
    all_labels = set(left) | set(right)
    
    # KL divergence approximation
    kl_div = 0.0
    for label in all_labels:

        p_left = left_dist.get(label, 0) / len(left)
        p_right = right_dist.get(label, 0) / len(right)
        
        if p_left > 0 and p_right > 0:
            kl_div += p_left * np.log2(p_left / p_right)
    
    # Return negative entropy (coherence) plus boundary strength
    return -(left_entropy + right_entropy) + kl_div
