from analysis.segmenters.cusum_segmenter import cusum_segmenter

def recursive_cusum_segmenter(sequence, z_score_threshold=3.0, depth=2):
    """Two-pass CUSUM for large datasets"""
    
    if depth < 1:
        return ValueError("Depth must be at least 1")

    if depth == 1:
        return cusum_segmenter(sequence, z_score_threshold)
    
    high_order_segments = cusum_segmenter(sequence, z_score_threshold)
    print(high_order_segments)
    
    return [
        recursive_cusum_segmenter(
            seg,
            z_score_threshold=z_score_threshold,
            depth=depth - 1
        )
        for seg in high_order_segments
    ]