
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.screener import ScreenerRequest, ScreenerResponse, ScreenerResult
from app.services.data_fetcher import DataFetcher
from app.engine.runner import BacktestEngine
from app.engine.sandbox import execute_strategy_code
from app.models.stock import StockBasic
import pandas as pd
from datetime import datetime, timedelta
import random

router = APIRouter()

# Hardcoded stock pool for performance testing
STOCK_POOL = [
    "000001", "600519", "000858", "600036", "002594",
    "300750", "300059", "601318", "600030", "000002"
]

@router.post("/screen", response_model=ScreenerResponse)
async def screen_stocks(request: ScreenerRequest, db: Session = Depends(get_db)):
    """
    Execute a strategy across a pool of stocks to identify buy signals.
    """

    # Calculate date range (Today - 90 days to ensure enough bars for indicators)
    today = datetime.now()
    if request.date:
        try:
            today = datetime.strptime(request.date, "%Y%m%d")
        except ValueError:
            pass

    start_date = (today - timedelta(days=90)).strftime("%Y%m%d")
    end_date = today.strftime("%Y%m%d")

    hits = []

    print(f"Screening {len(STOCK_POOL)} stocks from {start_date} to {end_date}")

    try:
        strategy_class = execute_strategy_code(request.strategy_code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Strategy compilation error: {str(e)}")

    for symbol in STOCK_POOL:
        try:
            # 1. Fetch Data
            df = DataFetcher.get_kline_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                period="daily",
                adjust="qfq"
            )

            if df.empty or len(df) < 10: # Ensure enough data
                continue

            # 2. Run Backtest
            engine = BacktestEngine(strategy_class, df, initial_cash=100000.0)
            engine.run()

            # 3. Check for Buy Signal on the LAST bar
            # Logic: If the engine executed a BUY trade on the last available date
            if not engine.broker.trades:
                continue

            last_trade = engine.broker.trades[-1]
            last_bar_date = df.index[-1]

            # Check if trade happened on the last bar (or very recent)
            # engine.broker.trades use datetime objects
            trade_date = last_trade.timestamp

            # Since trade timestamp matches bar timestamp (usually EOD or Open), check date equality
            if last_trade.side == 'buy' and trade_date.date() == last_bar_date.date():
                # Hit!
                # Fetch Name
                stock = db.query(StockBasic).filter(StockBasic.symbol == symbol).first()
                name = stock.name if stock else "Unknown"
                current_price = last_trade.price

                hits.append(ScreenerResult(
                    symbol=symbol,
                    name=name,
                    price=current_price,
                    signal_date=last_bar_date.strftime("%Y-%m-%d"),
                    signal_type="Buy"
                ))

        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            continue

    return ScreenerResponse(hits=hits)
