
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
    def get_stock_info(symbol: str) -> float:
        """
        Fetches total shares for a stock to calculate market cap.
        Returns total shares (float). Returns 0 if failed.
        """
        try:
            # stock_individual_info_em returns a dataframe with columns "item", "value"
            # item: 总股本
            df_info = ak.stock_individual_info_em(symbol=symbol)
            row = df_info[df_info['item'] == '总股本']
            if not row.empty:
                return float(row['value'].values[0])
            return 0.0
        except Exception as e:
            print(f"Error fetching stock info for {symbol}: {e}")
            return 0.0

    @staticmethod
    def get_kline_data(symbol: str, start_date: str, end_date: str, period: str = "daily", adjust: str = "qfq") -> pd.DataFrame:
        """
        Fetches historical k-line data for a specific stock.

        :param symbol: Stock symbol (e.g., "000001")
        :param start_date: Start date in "YYYYMMDD" format
        :param end_date: End date in "YYYYMMDD" format
        :param period: Period, e.g., "daily", "weekly", "monthly"
        :param adjust: Adjustment type, default "qfq" (forward adjusted)
        :return: DataFrame with historical data, standardized columns (date, open, close, high, low, volume, amount)
        """
        try:
            # ak.stock_zh_a_hist returns columns like: '日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率'
            df = ak.stock_zh_a_hist(symbol=symbol, period=period, start_date=start_date, end_date=end_date, adjust=adjust)

            if df is None or df.empty:
                return pd.DataFrame()

            # Rename columns to standard English names
            rename_map = {
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
            }
            df.rename(columns=rename_map, inplace=True)

            # Ensure date column is datetime and set as index
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)

            # Add symbol column if missing (useful for multi-symbol strategies later)
            if 'symbol' not in df.columns:
                df['symbol'] = symbol

            # Add total_shares for Market Cap calculation
            total_shares = DataFetcher.get_stock_info(symbol)
            df['total_shares'] = total_shares

            return df
        except Exception as e:
            print(f"Error fetching kline data for {symbol}: {e}")
            raise
