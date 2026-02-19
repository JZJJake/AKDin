
from pydantic import BaseModel, Field

class BacktestRequest(BaseModel):
    strategy_code: str = Field(..., title="The strategy code to execute")
    symbol: str = Field("000001", title="Stock symbol")
    start_date: str = Field("20230101", title="Start date YYYYMMDD")
    end_date: str = Field("20240101", title="End date YYYYMMDD")
    period: str = Field("daily", title="Timeframe: daily, weekly, monthly")
