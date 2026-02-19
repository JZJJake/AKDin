
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.models.stock import StockBasic
from app.schemas.stock import StockOut, PaginatedStocks
from typing import List, Optional

router = APIRouter()

@router.get("/stocks", response_model=PaginatedStocks)
def get_stocks(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    q: Optional[str] = Query(None, description="Search by symbol or name (fuzzy)")
):
    """
    Get a list of stocks with pagination and fuzzy search support.
    """
    query = db.query(StockBasic)

    if q:
        search = f"%{q}%"
        # Using ilike for case-insensitive search (Postgres)
        # For SQLite, LIKE is case-insensitive by default for ASCII only usually, but acceptable for demo
        query = query.filter(
            or_(
                StockBasic.symbol.ilike(search),
                StockBasic.name.ilike(search)
            )
        )

    total = query.count()
    stocks = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": stocks
    }
