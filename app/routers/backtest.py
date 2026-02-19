
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
        print(f"Fetching data for {request.symbol} from {request.start_date} to {request.end_date} (period={request.period})")
        df = DataFetcher.get_kline_data(
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            period=request.period,
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
        # Calculate Indicators (MA20, Volume MA5, MACD, KDJ)
        # 1. MA20
        df['ma20'] = df['close'].rolling(window=20).mean()

        # 2. Volume MA5
        if 'volume' in df.columns:
            df['vol_ma5'] = df['volume'].rolling(window=5).mean()

        # 3. MACD (12, 26, 9)
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd_dif'] = ema12 - ema26
        df['macd_dea'] = df['macd_dif'].ewm(span=9, adjust=False).mean()
        df['macd_bar'] = 2 * (df['macd_dif'] - df['macd_dea'])

        # 4. KDJ (9, 3, 3)
        low_min = df['low'].rolling(window=9).min()
        high_max = df['high'].rolling(window=9).max()
        rsv = (df['close'] - low_min) / (high_max - low_min) * 100
        # Pandas ewm com=2 is alpha=1/3
        df['kdj_k'] = rsv.ewm(alpha=1/3, adjust=False).mean()
        df['kdj_d'] = df['kdj_k'].ewm(alpha=1/3, adjust=False).mean()
        df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']

        # Convert index (date) to string for JSON serialization
        # Replace NaN with None for JSON compliance
        df_chart = df.reset_index()
        if 'date' in df_chart.columns:
            df_chart['date'] = df_chart['date'].dt.strftime('%Y-%m-%d')

        df_chart = df_chart.where(pd.notnull(df_chart), None)

        result["kline_data"] = df_chart.to_dict(orient="records")

        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Backtest failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
