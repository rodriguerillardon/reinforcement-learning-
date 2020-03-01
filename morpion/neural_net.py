import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset
from logzero import logger

import matplotlib
matplotlib.use("Agg")

class board_data(Dataset):
    def __init__(self, dataset):  # dataset = np.array of (s, p, v)
        logger.info(dataset)
        self.X = dataset[:, 0]
        self.y_p, self.y_v = dataset[:, 1], dataset[:, 2]

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return np.int64(self.X[idx].transpose(2, 0, 1)), self.y_p[idx], self.y_v[idx]

class ConvBlock(nn.Module):
    def __init__(self):
        super(ConvBlock,self).__init__()
        self.action_size = 3
        self.conv1 = nn.Conv2d(3,128,3, stride=1, padding=1)
        self.bn1 = nn.BatchNorm2d(128)

    def forward(self, s):
        s = s.view(-1,3,3,3) #reshape the tensor
        s = F.relu(self.bn1(self.conv1(s)))
        return s

class ResBlock(nn.Module):
    def __init__(self, inplanes=128, planes=128, stride=1):
        super(ResBlock, self).__init__()
        self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)

    def forward(self, x):
        residual = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = F.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        out += residual
        out = F.relu(out)
        return out

class OutBlock(nn.Module):
    def __init__(self):
        super(OutBlock, self).__init__()
        self.conv = nn.Conv2d(128, 3, kernel_size=1)
        self.bn = nn.BatchNorm2d(3)
        self.fc1 = nn.Linear(3*3*3, 32)
        self.fc2 = nn.Linear(32,1)

        self.conv1 = nn.Conv2d(128, 32, kernel_size=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.logsoftmax = nn.LogSoftmax(dim=1)
        self.fc = nn.Linear(3*3*32, 3)

    def forward(self, s):
        v = self.conv(s)
        v = self.bn(v)
        v = F.relu(v)
        v = v.view(-1, 3*3*3)
        v = self.fc1(v)
        v = F.relu(v)
        v = self.fc2(v)
        v = F.tanh(v)

        p = self.conv1(s)
        p = self.bn1(p)
        p = F.relu(p)
        p = p.view(-1, 3*3*32)
        p = self.fc(p)
        p = self.logsoftmax(p).exp()
        return p, v

class ConnectNet(nn.Module):
    def __init__(self):
        super(ConnectNet,self).__init__()
        self.conv = ConvBlock()
        for block in range(19):
            setattr(self, 'res%i' % block, ResBlock())
        self.outblock = OutBlock()

    def forward(self, s):
        s = self.conv(s)
        for block in range(19):
            s = getattr(self, 'res%i' % block)(s)
        s = self.outblock(s)
        return s

class AlphaLoss(nn.Module):
    def __init__(self):
        super(AlphaLoss, self).__init__()

    def forward(self, y_value, value, y_policy, policy):
        value_error = (value - y_value)**2
        policy_error = torch.sum((-policy*(1e-8 + y_policy.float()).float().log()),1)
        total_error = (value_error.view(-1).float() + policy_error).mean()
        return total_error






