from dataclasses import dataclass

@dataclass
class User:
    name: str
    phone: str
    id: int = None
