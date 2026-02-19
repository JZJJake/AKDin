
import akshare as ak
import pandas as pd
from typing import Optional

class DataFetcher:
    @staticmethod
    def get_stock_list_data() -> pd.DataFrame:
        """
        Fetches the latest A-share stock list using AkShare.
        Returns a DataFrame with columns including '代码', '名称', etc.
        """
        try:
            # stock_zh_a_spot_em returns the real-time quote for all A-shares
            df = ak.stock_zh_a_spot_em()
            return df
        except Exception as e:
            print(f"Error fetching stock list: {e}")
            raise

    @staticmethod
    def get_kline_data(symbol: str, start_date: str, end_date: str, period: str = "daily", adjust: str = "qfq") -> pd.DataFrame:
        """
        Fetches historical k-line data for a specific stock.

        :param symbol: Stock symbol (e.g., "000001")
        :param start_date: Start date in "YYYYMMDD" format
        :param end_date: End date in "YYYYMMDD" format
        :param period: Period, e.g., "daily", "weekly", "monthly"
        :param adjust: Adjustment type, default "qfq" (forward adjusted)
        :return: DataFrame with historical data
        """
        try:
            # ak.stock_zh_a_hist requires symbol as a string.
            # Note: AkShare might need just the 6-digit code or with market prefix depending on the function.
            # stock_zh_a_hist takes the 6 digit code usually.
            df = ak.stock_zh_a_hist(symbol=symbol, period=period, start_date=start_date, end_date=end_date, adjust=adjust)
            return df
        except Exception as e:
            print(f"Error fetching kline data for {symbol}: {e}")
            raise
