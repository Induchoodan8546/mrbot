
from dataclasses import dataclass


@dataclass
class ModelSettings:
    model: str
    temperature: float = 0.5
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    num_predict: int = 512
