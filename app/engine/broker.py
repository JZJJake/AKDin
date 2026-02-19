
from typing import Dict, List
from datetime import datetime
from app.engine.core import Position, Trade

class Broker:
    def __init__(self, initial_cash: float, commission_rate: float = 0.0003):
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.commission_rate = commission_rate
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = []

    def get_position(self, symbol: str) -> Position:
        return self.positions.get(symbol, Position(symbol, 0, 0.0))

    def buy(self, symbol: str, price: float, quantity: int, timestamp: datetime):
        if quantity <= 0:
            return

        cost = price * quantity
        commission = cost * self.commission_rate
        total_cost = cost + commission

        if self.cash >= total_cost:
            self.cash -= total_cost

            # Update position
            position = self.get_position(symbol)
            new_quantity = position.quantity + quantity
            new_avg_price = (position.average_price * position.quantity + cost) / new_quantity

            self.positions[symbol] = Position(symbol, new_quantity, new_avg_price, price)

            # Record trade
            self.trades.append(Trade(symbol, quantity, price, commission, timestamp, 'buy'))
        else:
            print(f"Insufficient funds to buy {quantity} {symbol} at {price}")

    def sell(self, symbol: str, price: float, quantity: int, timestamp: datetime):
        if quantity <= 0:
            return

        position = self.get_position(symbol)
        if position.quantity >= quantity:
            revenue = price * quantity
            commission = revenue * self.commission_rate
            net_revenue = revenue - commission

            self.cash += net_revenue

            # Update position
            new_quantity = position.quantity - quantity
            if new_quantity == 0:
                del self.positions[symbol]
            else:
                self.positions[symbol] = Position(symbol, new_quantity, position.average_price, price)

            # Record trade
            self.trades.append(Trade(symbol, quantity, price, commission, timestamp, 'sell'))
        else:
            print(f"Insufficient position to sell {quantity} {symbol}")

    def get_value(self, current_prices: Dict[str, float]) -> float:
        market_value = 0.0
        for symbol, position in self.positions.items():
            price = current_prices.get(symbol, position.average_price) # Fallback to last known price if current missing
            market_value += position.quantity * price
        return self.cash + market_value
