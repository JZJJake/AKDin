
from sqlalchemy import Column, String, Float, Date, Index
from app.models.base import Base

class StockBasic(Base):
    __tablename__ = "stock_basic"

    symbol = Column(String, primary_key=True, index=True, comment="股票代码")
    name = Column(String, index=True, comment="股票名称")
    # Industry might not be directly available in the main list, making it nullable for now
    industry = Column(String, nullable=True, comment="所属行业")
    list_date = Column(Date, nullable=True, comment="上市日期")

    # Adding a comprehensive index for search if needed, though individual indexes on symbol and name might suffice
    __table_args__ = (
        Index('ix_stock_basic_symbol_name', 'symbol', 'name'),
    )
