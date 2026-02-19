
from sqlalchemy import Column, Integer, String, DateTime, func, JSON
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import Base

class StrategyConfig(Base):
    __tablename__ = "strategy_config"

    id = Column(Integer, primary_key=True, index=True)
    strategy_code = Column(String, nullable=False, comment="策略代码")
    strategy_name = Column(String, nullable=False, comment="策略名称")
    # Use JSONB for PostgreSQL, JSON for others (like SQLite for testing)
    parameters = Column(JSON().with_variant(JSONB, 'postgresql'), nullable=False, comment="策略参数")
    user_id = Column(Integer, nullable=True, comment="用户ID")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
