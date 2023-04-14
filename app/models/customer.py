from dataclasses import dataclass
from typing import Optional


@dataclass
class Customer:
    first_name: str
    last_name: str
    phone_number: str
    address: str
    card: Optional[str] = None

    def is_regular(self):
        return self.card is not None
