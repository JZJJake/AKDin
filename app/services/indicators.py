
import pandas as pd

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate technical indicators (MA, Volume MA, MACD, KDJ) for a given DataFrame.
    Expects columns: 'close', 'volume', 'low', 'high'.
    """
    if df.empty:
        return df

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

    return df
