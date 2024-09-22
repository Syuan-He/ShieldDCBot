import torch
from torch import nn
from transformers import AutoTokenizer

from utils.DevConf import DevConf
from utils.AttnBlocksConf import AttnBlocksConf
from model.CombinationModel import CombinationModel

DEV_CONF = DevConf(device='cuda' if torch.cuda.is_available() else 'cpu')

class MyTrainer:
    def __init__(self, class_count: int, attention_config: AttnBlocksConf=AttnBlocksConf(768, 12, nKVHead=6)) -> None:
        self.class_count = class_count
        self.model = CombinationModel(class_count, attention_config, devConf=DEV_CONF)
        self.tokenizer = AutoTokenizer.from_pretrained("distilbert/distilbert-base-multilingual-cased", cache_dir='./cache/tokenizer')

    def inference(self, text: str) -> list:
        self.model.eval()
        with torch.no_grad():
            data = self.tokenizer(text, return_tensors='pt', padding='max_length', truncation=True, max_length=512).to(device=DEV_CONF.device)
            output = self.model(**data, NoGradBert=False).squeeze()
            return output[:, 1].tolist()

    def save(self, path: str = 'myModel.pth'):
        torch.save(self.model.state_dict(), path)

    def load(self, path: str):
        self.model.load_state_dict(torch.load(path, map_location=DEV_CONF.device))
