from dataclasses import dataclass


@dataclass
class ModelSettings:
    model: str
    temperature: float = 0.7