
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.models.stock import StockBasic
from app.schemas.stock import StockOut, PaginatedStocks, StockListResponse, KlineResponse
from app.services.data_fetcher import DataFetcher
from app.services.indicators import calculate_technical_indicators
from typing import List, Optional
import pandas as pd
from datetime import datetime, timedelta

router = APIRouter()

# Hardcoded popular stocks for robust demo
POPULAR_STOCKS = [
    {"symbol": "000001", "name": "平安银行"},
    {"symbol": "600519", "name": "贵州茅台"},
    {"symbol": "300750", "name": "宁德时代"},
    {"symbol": "002594", "name": "比亚迪"},
    {"symbol": "600036", "name": "招商银行"},
    {"symbol": "601318", "name": "中国平安"},
    {"symbol": "000858", "name": "五粮液"},
    {"symbol": "601888", "name": "中国中免"},
    {"symbol": "600276", "name": "恒瑞医药"},
    {"symbol": "300059", "name": "东方财富"},
    {"symbol": "000002", "name": "万科A"},
    {"symbol": "600030", "name": "中信证券"},
    {"symbol": "601012", "name": "隆基绿能"},
    {"symbol": "300015", "name": "爱尔眼科"},
    {"symbol": "002415", "name": "海康威视"},
    {"symbol": "603288", "name": "海天味业"},
    {"symbol": "600887", "name": "伊利股份"},
    {"symbol": "600900", "name": "长江电力"},
    {"symbol": "601628", "name": "中国人寿"},
    {"symbol": "000333", "name": "美的集团"},
    {"symbol": "000651", "name": "格力电器"},
    {"symbol": "601166", "name": "兴业银行"},
    {"symbol": "601328", "name": "交通银行"},
    {"symbol": "601288", "name": "农业银行"},
    {"symbol": "601398", "name": "工商银行"},
    {"symbol": "601939", "name": "建设银行"},
    {"symbol": "601988", "name": "中国银行"},
    {"symbol": "601857", "name": "中国石油"},
    {"symbol": "600028", "name": "中国石化"},
    {"symbol": "601088", "name": "中国神华"}
]

@router.get("/stocks/list", response_model=StockListResponse)
def get_stock_list():
    """
    Get a list of popular stocks for the sidebar.
    """
    return {"stocks": POPULAR_STOCKS}

@router.get("/stocks/{symbol}/kline", response_model=KlineResponse)
def get_stock_kline(
    symbol: str,
    period: str = Query("daily", regex="^(daily|weekly|monthly)$")
):
    """
    Get K-line data with indicators for a specific stock.
    """
    # Calculate start date (e.g. 2 years ago for enough history)
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=730)).strftime("%Y%m%d")

    try:
        df = DataFetcher.get_kline_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjust="qfq"
        )

        if df.empty:
             # Fallback for empty data or error
             return {"symbol": symbol, "kline_data": []}

        # Calculate Indicators
        df = calculate_technical_indicators(df)

        # Format for JSON
        df_chart = df.reset_index()
        if 'date' in df_chart.columns:
            df_chart['date'] = df_chart['date'].dt.strftime('%Y-%m-%d')

        df_chart = df_chart.where(pd.notnull(df_chart), None)

        return {
            "symbol": symbol,
            "kline_data": df_chart.to_dict(orient="records")
        }
    except Exception as e:
        print(f"Error fetching kline for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
