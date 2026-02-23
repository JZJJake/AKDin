
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import pandas as pd
from app.main import app
from datetime import datetime

client = TestClient(app)

class TestStocksAPI(unittest.TestCase):

    @patch('app.services.data_fetcher.DataFetcher.get_stock_info')
    def test_get_stock_list_and_info(self, mock_get_info):
        mock_get_info.return_value = 1000000.0 # Mock total shares

        response = client.get("/api/v1/stocks/list")
        self.assertEqual(response.status_code, 200)

    @patch('app.services.data_fetcher.DataFetcher.get_kline_data')
    def test_get_stock_kline(self, mock_get_kline):
        # Mock DataFetcher
        dates = pd.date_range(end=datetime.now(), periods=50)
        mock_df = pd.DataFrame({
            "close": [10.0] * 50,
            "open": [10.0] * 50,
            "high": [11.0] * 50,
            "low": [9.0] * 50,
            "volume": [1000] * 50,
            "total_shares": [1000000.0] * 50 # New column
        }, index=dates)
        mock_get_kline.return_value = mock_df

        response = client.get("/api/v1/stocks/000001/kline?period=daily")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Check for indicators
        first_bar = data["kline_data"][-1]
        self.assertIn("ma20", first_bar)

if __name__ == "__main__":
    unittest.main()
