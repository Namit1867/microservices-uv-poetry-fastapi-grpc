from dataclasses import dataclass
from typing import List

@dataclass
class Order:
    id: str
    user_id: str
    item: str
    total: float

_DB: List[Order] = [
    Order(id="o1", user_id="u1", item="Headphones", total=199.0),
    Order(id="o2", user_id="u1", item="Mic",        total=129.5),
    Order(id="o3", user_id="u2", item="Keyboard",   total=89.0),
]

def list_orders(user_id: str) -> list[Order]:
    return [o for o in _DB if o.user_id == user_id]
