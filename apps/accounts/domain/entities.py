from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserEntity:
    id: int
    username: str
    email: str
    phone_number: str
