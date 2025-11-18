"""
Neural Network

Small convolutionnal network
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class SmallNet(nn.Module):
    def __init__(self):
        super().__init__()
        # Input (batch, 2, 3, 3)
        self.conv1 = nn.Conv2d(2, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.fc_common = nn.Linear(64 * 3 * 3, 128)

        # Policy head
        self.policy_head = nn.Linear(128, 9)
        # Value head
        self.value_head = nn.Linear(128, 1)

    def forward(self, x):
        # x: [batch, 2, 3, 3]
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc_common(x))

        logits = self.policy_head(x)  # Raw logits for 9 moves
        value = torch.tanh(self.value_head(x)).squeeze(-1)  # in [-1, 1]

        return logits, value
