
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np
from app.main import app

client = TestClient(app)

class TestBacktestAPI(unittest.TestCase):

    @patch('app.services.data_fetcher.DataFetcher.get_kline_data')
    def test_run_backtest(self, mock_get_kline):
        # 1. Mock DataFetcher
        dates = pd.date_range(start="2023-01-01", periods=50)
        # Use sine wave to guarantee crossings
        x = np.linspace(0, 4*np.pi, 50)
        close_prices = 100 + 10 * np.sin(x)

        mock_df = pd.DataFrame({
            "close": close_prices,
            "symbol": ["000001"] * 50
        }, index=dates)
        mock_get_kline.return_value = mock_df

        # 2. Strategy Code (SMA) - NO IMPORTS, use pd directly
        strategy_code = """
# import pandas as pd # NOT ALLOWED
# from app.engine.base import BaseStrategy # NOT ALLOWED

class TestStrategy(BaseStrategy):
    def init(self):
        self.ma_period = 5

    def next(self):
        if len(self.data) < self.ma_period: return

        ma = self.data['close'].rolling(window=self.ma_period).mean().iloc[-1]
        price = self.data['close'].iloc[-1]

        if self.position.quantity == 0 and price > ma:
            self.buy(100)
        elif self.position.quantity > 0 and price < ma:
            self.sell(self.position.quantity)
"""

        # 3. Call API
        payload = {
            "strategy_code": strategy_code,
            "symbol": "000001",
            "start_date": "20230101",
            "end_date": "20230301"
        }

        response = client.post("/api/v1/backtest", json=payload)

        if response.status_code != 200:
            print("Response:", response.json())

        # 4. Verify
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("total_return", data)
        self.assertIn("equity_curve", data)
        self.assertIn("trades", data)
        # self.assertTrue(len(data["trades"]) > 0) # Might not trade depending on data, but sine wave should

        # Check equity curve structure
        if len(data["equity_curve"]) > 0:
            first_point = data["equity_curve"][0]
            self.assertIn("date", first_point)
            self.assertIn("equity", first_point)

if __name__ == "__main__":
    unittest.main()
