from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class WalletEntity:
    id: int
    user_id: int
    balance: float
    currency: str


@dataclass
class TransactionEntity:
    id: int
    sender_wallet_id: int
    receiver_wallet_id: int
    amount: float
    created_at: datetime
    status: str
    scheduled: Optional[datetime] = None
    event: str = ""
