
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import pandas as pd
from app.main import app as fastapi_app
from datetime import datetime
from app.core.database import get_db
# Import the module explicitly to ensure it is loaded for patching
import app.routers.screener

client = TestClient(fastapi_app)

class TestScreenerAPI(unittest.TestCase):

    def setUp(self):
        # Override dependency
        self.mock_db = MagicMock()
        fastapi_app.dependency_overrides[get_db] = lambda: self.mock_db

    def tearDown(self):
        fastapi_app.dependency_overrides = {}

    @patch('app.routers.screener.DataFetcher.get_kline_data')
    @patch('app.routers.screener.execute_strategy_code')
    def test_screener_hit(self, mock_execute, mock_get_kline):
        # 1. Mock Strategy Class (returns a mock class)
        MockStrategy = MagicMock()
        mock_execute.return_value = MockStrategy

        # 2. Mock Data (Need valid dataframe)
        dates = pd.date_range(end=datetime.now(), periods=60)
        mock_df = pd.DataFrame({
            "close": [10.0] * 60,
            "symbol": ["000001"] * 60,
            "open": [10.0] * 60,
            "high": [11.0] * 60,
            "low": [9.0] * 60,
        }, index=dates)
        mock_get_kline.return_value = mock_df

        # 3. Mock DB Query
        mock_stock = MagicMock()
        mock_stock.name = "Test Stock"
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_stock

        with patch('app.routers.screener.BacktestEngine') as MockEngine:
            # Configure the mock engine instance
            mock_engine_instance = MockEngine.return_value
            mock_engine_instance.run.return_value = {} # Run returns dict

            # Mock the broker and trades
            mock_broker = MagicMock()
            # Create a fake trade on the last date
            last_date = dates[-1]
            mock_trade = MagicMock()
            mock_trade.side = 'buy'
            mock_trade.timestamp = last_date
            mock_trade.price = 10.5

            mock_broker.trades = [mock_trade]
            mock_engine_instance.broker = mock_broker

            # 4. Call API
            payload = {
                "strategy_code": "pass", # Code doesn't matter as we mock execution
            }

            response = client.post("/api/v1/screen", json=payload)

            # 5. Verify
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("hits", data)

            self.assertTrue(len(data["hits"]) > 0)
            first_hit = data["hits"][0]
            self.assertEqual(first_hit["signal_type"], "Buy")
            self.assertEqual(first_hit["price"], 10.5)
            self.assertEqual(first_hit["name"], "Test Stock")

if __name__ == "__main__":
    unittest.main()
