import backtrader as bt


class BuyHold(bt.Strategy):
    def __init__(self):
        self.stock = self.datas[0]
        self.buy_size = 5
        self.buy_price = None

    def next(self):
        if self.buy_price is None:
            # Place a buy order at the current price
            self.buy_price = self.stock.close[0]
            self.order_target_percent(target=0.95)

        # Hold the position until the end of the backtest
        self.hold()

    def hold(self):
        if self.data.datetime.date(0) == self.datas[0].datetime.date(-1):
            self.close()
