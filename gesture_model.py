import torch
import torch.nn as nn

class GestureTransformer(nn.Module):
    def __init__(self, input_dim, model_dim=128, num_heads=4, num_layers=2, output_dim=6):
        super().__init__()
        self.embedding = nn.Linear(input_dim, model_dim)
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(model_dim, num_heads), num_layers
        )
        self.fc = nn.Linear(model_dim, output_dim)

    def forward(self, x):
        x = self.embedding(x)
        x = x.permute(1, 0, 2)
        x = self.transformer(x)
        x = x.mean(dim=0)
        return self.fc(x)