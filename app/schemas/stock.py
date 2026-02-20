
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import date

# --- Legacy Schemas ---
class StockBase(BaseModel):
    symbol: str = Field(..., title="股票代码")
    name: str = Field(..., title="股票名称")
    industry: Optional[str] = Field(None, title="所属行业")
    list_date: Optional[date] = Field(None, title="上市日期")

class StockOut(StockBase):
    class Config:
        from_attributes = True

class PaginatedStocks(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[StockOut]

# --- New Schemas ---
class StockListItem(BaseModel):
    symbol: str
    name: str

class StockListResponse(BaseModel):
    stocks: List[StockListItem]

class KlineResponse(BaseModel):
    symbol: str
    kline_data: List[Dict[str, Any]]
