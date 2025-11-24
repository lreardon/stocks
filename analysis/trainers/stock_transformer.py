import torch
import torch.nn as nn

class StockTransformer(nn.Module):
    def __init__(
        self,
        d_model=100,
        nhead=4,
        num_layers=4,
        dim_feedforward=512
    ):
        super().__init__()
        
        # Positional encoding
        self.pos_encoder = nn.Parameter(torch.randn(1, 50, d_model))
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Output head - predict next window
        self.output_head = nn.Linear(d_model, d_model)
        
    def forward(self, x):
        # x shape: (batch, 50, 100)
        
        # Add positional encoding
        x = x + self.pos_encoder
        
        # Pass through transformer
        x = self.transformer(x)
        
        # Take the last token's output and project to target dimension
        x = x[:, -1, :]  # Shape: (batch, 100)
        x = self.output_head(x)
        
        return x