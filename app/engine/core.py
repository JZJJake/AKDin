
from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime

@dataclass
class Position:
    symbol: str
    quantity: int
    average_price: float
    current_price: float = 0.0

@dataclass
class Trade:
    symbol: str
    quantity: int
    price: float
    commission: float
    timestamp: datetime
    side: str  # 'buy' or 'sell'
