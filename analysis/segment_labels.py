# from pathlib import Path
# # from analysis.tokenization.segmentation.mutual_info_segmentation import sliding_window_segmentation
# from collections import Counter


# def collapse_runs(sequence):
#     """Collapse consecutive identical symbols into single instances."""
#     if not sequence:
#         return sequence
    
#     result = [sequence[0]]
    
#     for symbol in sequence[1:]:
#         if symbol != result[-1]:
#             result.append(symbol)
    
#     return ''.join(result) if isinstance(sequence, str) else result

# cwd = Path.cwd()

# with open(cwd/'data'/'SPY'/'analysis'/'historical_pct'/'encoded_sequence.txt', 'r') as f:
#     encoded_sequence = f.read()

# collapsed_sequence = collapse_runs(encoded_sequence)

# print(len(collapsed_sequence))

# tokens, boundaries = sliding_window_segmentation(collapsed_sequence, window_size=len(collapsed_sequence), step_size=len(collapsed_sequence), min_token_length=2)

# token_counts = Counter(tokens)

# for token, count in token_counts.most_common(10):
#         print(f"  {repr(token)}: {count} times")
    