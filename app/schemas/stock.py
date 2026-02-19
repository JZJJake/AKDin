
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

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
