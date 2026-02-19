
from fastapi import APIRouter, HTTPException
from app.schemas.backtest import BacktestRequest
from app.services.data_fetcher import DataFetcher
from app.engine.runner import BacktestEngine
from app.engine.sandbox import execute_strategy_code
import pandas as pd
from typing import Dict, Any

router = APIRouter()

@router.post("/backtest")
async def run_backtest(request: BacktestRequest) -> Dict[str, Any]:
    """
    Execute a backtest given a strategy code and parameters.
    """
    try:
        # 1. Fetch historical data
        print(f"Fetching data for {request.symbol} from {request.start_date} to {request.end_date}")
        df = DataFetcher.get_kline_data(
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            period="daily",
            adjust="qfq"
        )

        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {request.symbol} in the specified range.")

        # 2. Execute strategy code to get the class
        print("Compiling strategy code...")
        try:
            strategy_class = execute_strategy_code(request.strategy_code)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Strategy compilation error: {str(e)}")

        # 3. Instantiate Engine and Run
        print("Running backtest engine...")
        engine = BacktestEngine(strategy_class, df, initial_cash=100000.0)
        result = engine.run()

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        # Inject kline_data for frontend charting
        # Convert index (date) to string for JSON serialization
        df_chart = df.reset_index()
        if 'date' in df_chart.columns:
            df_chart['date'] = df_chart['date'].dt.strftime('%Y-%m-%d')

        result["kline_data"] = df_chart.to_dict(orient="records")

        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Backtest failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
