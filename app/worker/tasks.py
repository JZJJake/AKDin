
from app.worker.celery_app import celery_app
from app.services.notification import PushPlusNotifier
import time
import pandas as pd

def is_trading_hours() -> bool:
    """
    Check if the current time is within A-share trading hours.
    Trading Hours: Mon-Fri, 09:30-11:30, 13:00-15:00 (Asia/Shanghai)
    """
    now = pd.Timestamp.now(tz='Asia/Shanghai')

    # Check if weekday (Monday=0, Sunday=6)
    if now.dayofweek > 4:
        return False

    current_time = now.time()

    # Define trading sessions
    morning_start = pd.Timestamp("09:30").time()
    morning_end = pd.Timestamp("11:30").time()
    afternoon_start = pd.Timestamp("13:00").time()
    afternoon_end = pd.Timestamp("15:00").time()

    is_morning = morning_start <= current_time <= morning_end
    is_afternoon = afternoon_start <= current_time <= afternoon_end

    return is_morning or is_afternoon

@celery_app.task
def run_strategy_monitor():
    """
    Monitor running strategies for signals (Unified with Screener Logic).
    Checks trading hours before execution.
    Current Architecture: Stateless Window Run.
    """
    if not is_trading_hours():
        print("[Task] Market closed, skipping execution.")
        return "Market closed"

    print("[Task] Starting strategy monitor (Screener Mode)...")

    # 1. Fetch live tick (dummy)
    # real_time_quotes = DataFetcher.get_real_time_quotes(stock_pool)

    # 2. Window Run (dummy) - Treat as Screener
    # for stock in stock_pool:
    #     history = DataFetcher.get_kline_data(stock, limit=60)
    #     engine = BacktestEngine(strategy, history + tick)
    #     engine.run()
    #     if engine.new_orders:
    #         alerts.append(...)

    # 3. Trigger PushPlusNotifier.send("Alert", "Buy Signal on 000001")
    # This is a dummy alert to verify the pipeline

    # Simulate some processing time
    time.sleep(1)

    title = "Strategy Alert"
    content = "Buy Signal on 000001 (Simulated)"
    print(f"[Task] Triggering notification: {title}")

    # In production, we would only send if a signal actually happened.
    # For now, we don't spam the user's phone unless we have a real token,
    # but the Notifier class handles the dummy token gracefully by printing.
    PushPlusNotifier.send(title, content)

    return "Monitor run complete"
