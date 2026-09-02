import torch
import torch.nn as nn
import torch.nn.functional as F

class Conv1x1(nn.Module):
    def __init__(self, in_c, out_c):
        super().__init__()
        self.conv = nn.Conv2d(in_c, out_c, 1, bias=False)
        self.bn = nn.BatchNorm2d(out_c)
        self.relu = nn.ReLU(inplace=True)
    def forward(self, x):
        return self.relu(self.bn(self.conv(x)))

class OSBlock(nn.Module):
    """
    Omni-Scale Residual Block: aggregates multi-scale receptive fields (1x1, 3x3, 5x5).
    """
    def __init__(self, in_c, out_c):
        super().__init__()
        mid_c = out_c // 4
        self.reduce = Conv1x1(in_c, mid_c)
        
        # Scale 1: 3x3
        self.stream1 = nn.Sequential(
            nn.Conv2d(mid_c, mid_c, 3, padding=1, bias=False),
            nn.BatchNorm2d(mid_c),
            nn.ReLU(inplace=True)
        )
        # Scale 2: 3x3 stacked = 5x5 effective
        self.stream2 = nn.Sequential(
            nn.Conv2d(mid_c, mid_c, 3, padding=1, bias=False),
            nn.BatchNorm2d(mid_c),
            nn.ReLU(inplace=True),
            nn.Conv2d(mid_c, mid_c, 3, padding=1, bias=False),
            nn.BatchNorm2d(mid_c),
            nn.ReLU(inplace=True)
        )
        # Scale 3: 3x3 stacked 3 times = 7x7 effective
        self.stream3 = nn.Sequential(
            nn.Conv2d(mid_c, mid_c, 3, padding=1, bias=False),
            nn.BatchNorm2d(mid_c),
            nn.ReLU(inplace=True),
            nn.Conv2d(mid_c, mid_c, 3, padding=1, bias=False),
            nn.BatchNorm2d(mid_c),
            nn.ReLU(inplace=True),
            nn.Conv2d(mid_c, mid_c, 3, padding=1, bias=False),
            nn.BatchNorm2d(mid_c),
            nn.ReLU(inplace=True)
        )
        
        self.out_conv = Conv1x1(mid_c * 3, out_c)
        self.shortcut = Conv1x1(in_c, out_c) if in_c != out_c else nn.Identity()

    def forward(self, x):
        res = self.shortcut(x)
        x_red = self.reduce(x)
        s1 = self.stream1(x_red)
        s2 = self.stream2(x_red)
        s3 = self.stream3(x_red)
        merged = torch.cat([s1, s2, s3], dim=1)
        out = self.out_conv(merged)
        return F.relu(out + res)

class OSNetReID(nn.Module):
    """
    OSNet: Omni-Scale Feature Learning for Person Re-Identification.
    Takes full body image (256x128) and produces 512-D L2 normalized embedding.
    """
    def __init__(self, embedding_dim: int = 512):
        super().__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        )
        self.stage1 = OSBlock(64, 128)
        self.stage2 = OSBlock(128, 256)
        self.stage3 = OSBlock(256, 512)
        
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512, embedding_dim, bias=False)
        self.bn = nn.BatchNorm1d(embedding_dim)

    def forward(self, x):
        x = self.conv1(x)
        x = self.stage1(x)
        x = self.stage2(x)
        x = self.stage3(x)
        x = self.global_pool(x)
        x = torch.flatten(x, 1)
        x = self.bn(self.fc(x))
        return F.normalize(x, p=2, dim=1)
