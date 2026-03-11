"""
The Brain class to build the Agent model.
"""

import torch.nn as nn
import torch


class Brain(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(9, 27),
            nn.Softplus(),
            nn.Linear(27, 27),
            nn.Softplus(),
            nn.Linear(27, 9)
        )

    def forward(self, x):
        return self.model(x)


def load_params(model: nn.Module, genome: torch.Tensor) -> None:
    index = 0
    for p in model.parameters():
        size = p.numel()
        p.data.copy_(genome[index:index + size].view_as(p))
        index += size


"""class Brain(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.Softmax(),

            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.Softmax()
        )

        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(32 * 3 * 3, 64),
            nn.Softmax(),
            nn.Linear(64, 9)
        )

    def forward(self, x):
        x = self.conv(x)
        x = self.fc(x)
        return x"""
