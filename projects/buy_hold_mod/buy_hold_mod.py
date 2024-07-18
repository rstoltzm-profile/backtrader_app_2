import backtrader as bt


class BuyHoldMod(bt.Strategy):
    params = (
        ('printlog', False),
        ('period', 20)
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.days = 0
        self.trade_count = 0
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = 0
        self.buycomm = None

        # Return Values
        self.buy_sell_signals = []
        self.last_signal = None
        self.last_signal_date = None

        # Add a MovingAverageSimple indicator
        self.rsi = bt.indicators.RSI(self.data, period=self.p.period)
        self.tr = bt.indicators.TR(self.data)
        self.atr = bt.indicators.ATR(self.data, period=self.p.period)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        current_date = self.data.datetime.date()
        self.days = self.days + 1

        buyPattern1 = self.rsi < 40
        buyPattern2 = self.tr[0] > self.atr[0]

        sellPattern1 = self.rsi > 80
        sellPattern2 = False

        buyCheck = buyPattern1 and buyPattern2

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        if buyCheck and not self.position:
            self.buyprice = self.data.close[0]
            self.order_target_percent(target=0.95)
            self.trade_count = self.trade_count + 1

        elif self.position and (sellPattern1 or sellPattern2):
            self.order_target_percent(target=0.0)
            self.trade_count = self.trade_count - 1

        self.log(current_date)
