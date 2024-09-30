from src.type import ModelType
from typing import Optional

class SwitchManager:
    def __init__(self) -> None:
        self.switch_state: dict = {}

    def set_switch(self, guild_id: int, channel_id: int ,type: str, state: bool) -> None:
        self._set_default(guild_id, channel_id)
        self.switch_state[guild_id][channel_id][type] = state

    def get_switch(self, guild_id: int, channel_id: int ,type: str) -> bool:
        self._set_default(guild_id, channel_id)
        return self.switch_state[guild_id][channel_id][type]

    def get_all_switch(self, guild_id: int, channel_id: int) -> dict[ModelType, bool]:
        self._set_default(guild_id, channel_id)
        return {
            ModelType.Dangerous: self.switch_state[guild_id][channel_id][ModelType.Dangerous.value],
            ModelType.Harassment: self.switch_state[guild_id][channel_id][ModelType.Harassment.value],
            ModelType.Hate_Speech: self.switch_state[guild_id][channel_id][ModelType.Hate_Speech.value],
            ModelType.Sexually: self.switch_state[guild_id][channel_id][ModelType.Sexually.value]
        }
    
    def set_threshold(self, guild_id: int, type: str, threshold: float):
        self._set_default(guild_id)
        self.switch_state[guild_id][type] = threshold if threshold >= 0 and threshold <= 1 else 0.5

    def get_threshold(self, guild_id: int, type: str) -> float:
        self._set_default(guild_id)
        return self.switch_state[guild_id][type]

    def get_all_threshold(self, guild_id: int) -> dict[ModelType, bool]:
        self._set_default(guild_id=guild_id)
        return {
            ModelType.Dangerous: self.switch_state[guild_id][ModelType.Dangerous.value],
            ModelType.Harassment: self.switch_state[guild_id][ModelType.Harassment.value],
            ModelType.Hate_Speech: self.switch_state[guild_id][ModelType.Hate_Speech.value],
            ModelType.Sexually: self.switch_state[guild_id][ModelType.Sexually.value]
        }
    
    def is_open(self, guild_id: int, channel_id: int) -> bool:
        self._set_default(guild_id, channel_id)
        if (self.switch_state[guild_id][ModelType.Dangerous.value] == 0 and \
            self.switch_state[guild_id][ModelType.Harassment.value] == 0 and \
            self.switch_state[guild_id][ModelType.Hate_Speech.value] == 0 and \
            self.switch_state[guild_id][ModelType.Sexually.value] == 0 \
                ):
            return False
        
        if (self.switch_state[guild_id][channel_id][ModelType.Dangerous.value] == False and \
            self.switch_state[guild_id][channel_id][ModelType.Harassment.value] == False and \
            self.switch_state[guild_id][channel_id][ModelType.Hate_Speech.value] == False and \
            self.switch_state[guild_id][channel_id][ModelType.Sexually.value] == False \
                ):
            return False
        
        return True

    def _set_default(self, guild_id: int, channel_id: Optional[int] = None)->None:
        self.switch_state.setdefault(guild_id, {
            ModelType.Dangerous.value: 0.5,
            ModelType.Harassment.value: 0.5,
            ModelType.Hate_Speech.value: 0.5,
            ModelType.Sexually.value: 0.5,
        })
        if (channel_id is not None):
            self.switch_state[guild_id].setdefault(channel_id,{
                ModelType.Dangerous.value: True,
                ModelType.Harassment.value: True,
                ModelType.Hate_Speech.value: True,
                ModelType.Sexually.value: True
            })
