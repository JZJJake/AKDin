
from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, Any
from app.engine.broker import Broker

class BaseStrategy(ABC):
    def __init__(self, broker: Broker, data: pd.DataFrame):
        self.broker = broker
        self._data = data
        self.current_idx = 0
        self.init()

    @abstractmethod
    def init(self):
        """
        Initialize strategy parameters and indicators.
        """
        pass

    @abstractmethod
    def next(self):
        """
        Called for each bar in the data.
        """
        pass

    @property
    def data(self):
        """
        Returns a slice of the data up to the current index.
        For performance, this could be optimized, but slicing is safe.
        """
        # Return a view up to current_idx
        # Use .iloc which is position-based
        return self._data.iloc[:self.current_idx + 1]

    def buy(self, quantity: int = 100):
        """
        Place a market buy order at the current close price.
        """
        current_price = self.data['close'].iloc[-1]
        timestamp = self.data.index[-1]
        self.broker.buy(self.data['symbol'].iloc[-1], current_price, quantity, timestamp)

    def sell(self, quantity: int = 100):
        """
        Place a market sell order at the current close price.
        """
        current_price = self.data['close'].iloc[-1]
        timestamp = self.data.index[-1]
        self.broker.sell(self.data['symbol'].iloc[-1], current_price, quantity, timestamp)

    @property
    def position(self):
        """
        Returns the current position for the symbol being traded.
        """
        symbol = self.data['symbol'].iloc[-1]
        return self.broker.get_position(symbol)
