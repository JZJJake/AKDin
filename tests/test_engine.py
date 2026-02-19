
import unittest
import pandas as pd
import numpy as np
from datetime import datetime
from app.engine.runner import BacktestEngine
from app.engine.sandbox import execute_strategy_code
from app.engine.base import BaseStrategy

class TestBacktestEngine(unittest.TestCase):
    def setUp(self):
        # Create a sample DataFrame
        dates = pd.date_range(start="2023-01-01", periods=100)
        # Add some volatility to make SMA cross
        # For simplicity: linear trend up, but we want a strategy to work.
        # Let's create a sine wave + trend
        # close_prices = 100 + np.arange(100) + 10 * np.sin(np.arange(100) * 0.2)

        # Use simple sine wave to guarantee crossings
        x = np.linspace(0, 4*np.pi, 100)
        close_prices = 100 + 10 * np.sin(x)

        self.data = pd.DataFrame({
            "close": close_prices,
            "symbol": ["TEST"] * 100
        }, index=dates)

        # Simple SMA Strategy Code
        # Note: 'pd' is already injected into the scope by the sandbox.
        self.strategy_code = """
class SMAStrategy(BaseStrategy):
    def init(self):
        self.sma_period = 10

    def next(self):
        # Need enough data
        if len(self.data) < self.sma_period:
            return

        # Calculate SMA
        # self.data is a slice up to current bar
        sma = self.data['close'].rolling(window=self.sma_period).mean().iloc[-1]
        current_price = self.data['close'].iloc[-1]

        # Simple Logic: If price > SMA and no position, buy.
        # If price < SMA and have position, sell.

        pos = self.position

        # Log for debugging (print is allowed)
        # print(f"Date: {self.data.index[-1]}, Price: {current_price}, SMA: {sma}")

        if pos.quantity == 0:
            if current_price > sma:
                self.buy(100)
        elif pos.quantity > 0:
            if current_price < sma:
                self.sell(pos.quantity)
"""

    def test_backtest_execution(self):
        # 1. Execute the strategy code to get the class
        strategy_class = execute_strategy_code(self.strategy_code)

        # 2. Run the backtest
        engine = BacktestEngine(strategy_class, self.data, initial_cash=100000.0)
        results = engine.run()

        # 3. Verify results
        # print("Backtest Results:", results)

        self.assertIn("total_return", results)
        self.assertIn("max_drawdown", results)

        # Ensure trades were made (sine wave guarantees crossings)
        if not results.get("trades"):
             print("No trades were made. Check strategy logic or data.")

        self.assertTrue(len(results["trades"]) > 0, "No trades were executed")

        # Verify first trade details
        first_trade = results["trades"][0]
        self.assertEqual(first_trade['symbol'], "TEST")
        self.assertEqual(first_trade['quantity'], 100)
        self.assertEqual(first_trade['side'], 'buy')

if __name__ == "__main__":
    unittest.main()
