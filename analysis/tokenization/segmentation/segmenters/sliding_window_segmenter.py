import numpy as np
# from analysis.tokenization.segmentation.boundary_scores.mutual_info_two import boundary_score_two

"""
Segment sequence using sliding window MI analysis.

Args:
    boundary_score: Function to score boundary between two segments
    symbols: String of symbols
    window_size: Size of analysis window
    step_size: Step size for sliding window
    min_token_length: Minimum token length
"""
def sliding_window_segmenter(
        boundary_score,
        window_size=500,
        step_size=50,
        min_token_length=3
    ):
    def _find_best_split(window, min_length):
        """Find the best split point in a window using MI."""
        n = len(window)
        best_score = -np.inf
        best_split = None
        
        for split in range(min_length, n - min_length + 1):
            print(split)
            left = window[:split]
            right = window[split:]
            
            # Calculate MI between left and right segments
            score = boundary_score(left, right)
            
            if score > best_score:
                best_score = score
                best_split = split
        
        return best_split
    
    def _segmenter(sequence: str):
        n = len(sequence)
        
        # Find candidate boundaries
        boundaries = []
        
        for start in range(0, n - window_size + 1, step_size):
            end = min(start + window_size, n)
            window = sequence[start:end]
            
            # Find best split point in this window
            best_split = _find_best_split(window, min_token_length)
            
            if best_split is not None:
                boundaries.append(start + best_split)
        
        # Remove duplicate boundaries and sort
        boundaries = sorted(list(set([0] + boundaries + [n])))
        
        # Extract tokens
        tokens = []
        for i in range(len(boundaries) - 1):
            print(i)

            token = sequence[boundaries[i]:boundaries[i+1]]
            if len(token) >= min_token_length:
                tokens.append(token)
        
        return tokens, boundaries
    
    return _segmenter