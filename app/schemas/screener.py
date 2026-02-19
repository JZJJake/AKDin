
from pydantic import BaseModel, Field
from typing import List

class ScreenerRequest(BaseModel):
    strategy_code: str = Field(..., title="The strategy code to execute")
    date: str = Field(None, title="Optional screening date (default today)")

class ScreenerResult(BaseModel):
    symbol: str
    name: str
    price: float
    signal_date: str
    signal_type: str = "Buy"

class ScreenerResponse(BaseModel):
    hits: List[ScreenerResult]
