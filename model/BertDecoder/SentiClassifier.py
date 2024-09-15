from typing import Optional

import torch
from torch import nn, Tensor
from einops import repeat
from transformers.modeling_outputs import BaseModelOutput

from utils.AttnBlocksConf import AttnBlocksConf
from utils.DevConf import DevConf
from module.blocks.CACBlocks import CACBlocks

class SentiClassifier(nn.Module):
    def __init__(
            self,
            layerNum: int,
            conf: AttnBlocksConf,
            devConf: DevConf=DevConf()
        ):
        super(SentiClassifier, self).__init__()

        if layerNum < 1:
            raise ValueError('layerNum must be greater than 0')
        else:
            self.mapper = CACBlocks(layerNum, conf, devConf)
        self.IsNeedHiddenState = True
        self._Q = nn.Linear(1, conf.hidDim, bias=False, device=devConf.device, dtype=devConf.dtype)
        self.token = nn.Parameter(torch.tensor([1], device=devConf.device, dtype=devConf.dtype), requires_grad=False)
        self._layerNum = layerNum
        self._devConf = devConf

    def forward(self,
                x: BaseModelOutput,
                returnAttnWeight: bool=False
                )->tuple[Tensor, Optional[Tensor]]:

        batch = x.last_hidden_state.size(0)
        q = self._Q(self.token)
        sentVec, attnWeight = self.mapper.forward(repeat(q, "d -> b l d", b=batch, l=1), x, need_weights=True)
        
        if returnAttnWeight:
            return sentVec.squeeze(1), attnWeight
        return sentVec.squeeze(1)
    