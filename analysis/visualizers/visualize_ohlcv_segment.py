import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np
from matplotlib.colors import Normalize

def visualize_scaled_close_and_volume_segment(segment: pd.DataFrame):
    _fig: Figure
    ax: Axes
    _fig, ax = plt.subplots(figsize=(12, 6))
    
    # Logarithmic scaling with color capped at e^15
    _log_volume = np.log(segment['volume'] + 1)  # +1 to handle volume=0
    volume_norm = (segment['volume'] - segment['volume'].min()) / (segment['volume'].max() - segment['volume'].min())
    
    # Create color map: blue (0 volume) to red (e^15+ volume)
    colors: list = plt.cm.coolwarm(volume_norm)

    for i in range(len(segment) - 1):
       ax.plot([i, i+1], [segment['close'].iloc[i], segment['close'].iloc[i+1]], 
               color=colors[i], linewidth=1.5)
    
    ax.set_title('Close Price (Color = Volume)')
    ax.set_xlabel('Index')
    ax.set_ylabel('Close Price')
    ax.grid(True, alpha=0.3)
    
    sm = plt.cm.ScalarMappable(cmap='coolwarm', norm=Normalize(vmin=segment['volume'].min(), vmax=segment['volume'].max()))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label('Volume')
    
    plt.tight_layout()
    plt.show()