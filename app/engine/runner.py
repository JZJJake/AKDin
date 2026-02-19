
import pandas as pd
from typing import Dict, Any, Type
from app.engine.base import BaseStrategy
from app.engine.broker import Broker

class BacktestEngine:
    def __init__(self, strategy_class: Type[BaseStrategy], data: pd.DataFrame, initial_cash: float = 100000.0, commission: float = 0.0003):
        self.strategy_class = strategy_class
        self.data = data
        self.initial_cash = initial_cash
        self.commission = commission
        self.broker = Broker(initial_cash, commission)
        self.strategy: BaseStrategy = None

    def run(self) -> Dict[str, Any]:
        """
        Runs the backtest event loop.
        """
        # Ensure data is sorted by date/index
        if not self.data.index.is_monotonic_increasing:
            self.data = self.data.sort_index()

        # Instantiate strategy
        # Pass a reference to the full data, but the strategy logic will slice it internally via .data property
        # Wait, BaseStrategy.data relies on self.current_idx.
        # We need to initialize the strategy instance.
        self.strategy = self.strategy_class(self.broker, self.data)

        equity_curve = []

        # Event Loop
        # We start from index 0. However, indicators usually need a warmup period.
        # We'll just run from 0 to len-1. The strategy is responsible for checking if enough data exists (e.g. len(self.data) > 20).
        total_steps = len(self.data)

        for i in range(total_steps):
            # Update strategy's current index pointer
            self.strategy.current_idx = i

            # Get current bar info for broker valuation
            current_date = self.data.index[i]
            # Assuming 'close' column exists
            current_close = self.data['close'].iloc[i]
            current_symbol = self.data['symbol'].iloc[i] if 'symbol' in self.data.columns else 'UNKNOWN'

            # Execute strategy logic
            self.strategy.next()

            # Record Equity
            # Current value is cash + value of holdings at current close
            # Simplified: assuming single symbol for now or passed data is single symbol
            current_prices = {current_symbol: current_close}
            total_value = self.broker.get_value(current_prices)
            equity_curve.append({
                "date": current_date,
                "equity": total_value,
                "cash": self.broker.cash
            })

        # Calculate Performance Metrics
        df_equity = pd.DataFrame(equity_curve)
        if df_equity.empty:
            return {"error": "No data processed"}

        final_value = df_equity['equity'].iloc[-1]
        total_return = (final_value - self.initial_cash) / self.initial_cash

        # Max Drawdown
        df_equity['max_equity'] = df_equity['equity'].cummax()
        df_equity['drawdown'] = (df_equity['equity'] - df_equity['max_equity']) / df_equity['max_equity']
        max_drawdown = df_equity['drawdown'].min()

        return {
            "initial_cash": self.initial_cash,
            "final_value": final_value,
            "total_return": total_return,
            "max_drawdown": max_drawdown,
            "equity_curve": df_equity[['date', 'equity']].to_dict(orient='records'),
            "trades": [t.__dict__ for t in self.broker.trades]
        }
