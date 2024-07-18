import backtrader as bt
import pandas as pd


class SmaExpCon(bt.Strategy):
    params = (
        ('printlog', True),
        ('hma_period', 49),
        ('atr_period', 50),
        ('buy_lag', 6),
        ('RangeStopLossMultiple', 2.5),
        ('ChannelStopLossMultiple', 0.97),
        ('DisasterStopLossMultiple', 0.90),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Parameters
        self.moving_averages_close = []
        self.moving_averages_high = []
        self.moving_averages_low = []
        self.ma_lengths = [6, 18]
        self.prev_close_price = 0
        self.compare_price = 0
        self.minperiod = 50

        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = 0
        self.buycomm = None

        # Return Values
        self.buy_sell_signals = []
        self.last_signal = None
        self.last_signal_date = None
        SMA = bt.indicators.SimpleMovingAverage

        for i in range(len(self.ma_lengths)):
            sma_close = SMA(self.data.close, period=self.ma_lengths[i])
            self.moving_averages_close.append(sma_close)

            sma_high = SMA(self.data.high, period=self.ma_lengths[i])
            self.moving_averages_high.append(sma_high)

            sma_low = SMA(self.data.low, period=self.ma_lengths[i])
            self.moving_averages_low.append(sma_low)
            print(sma_low)

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
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

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
        if len(self) < self.minperiod:
            return
        current_date = self.data.datetime.date()

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        buy_check = False
        sell_check = False

        # variables
        short_mah = self.moving_averages_high[0][0]
        short_mal = self.moving_averages_low[0][0]
        short_mac = self.moving_averages_close[0][0]

        long_mah = self.moving_averages_high[1][0]
        long_mal = self.moving_averages_low[1][0]
        long_mac = self.moving_averages_close[1][0]

        print(short_mah)
        print(long_mah)

        short_diff = (short_mah - short_mal)
        long_diff = (long_mah - long_mal)
        short_close = short_mac
        long_close = long_mac

        buy_check1 = short_diff > long_diff and short_close > long_close
        buy_check2 = short_diff < long_diff and short_close < long_close
        sell_check1 = short_diff < long_diff and short_close > long_close
        sell_check2 = short_diff > long_diff and short_close < long_close
        buy_check = buy_check1 or buy_check2
        sell_check = sell_check1 or sell_check2

        if not self.position and buy_check:
            self.prev_close_price = self.data.close[0]
            self.order = self.order_target_percent(target=0.95)
            self.buyprice = self.data.close[0]
            self.buy_sell_signals.append({"date": current_date,
                                          "signal": "BUY"})
        elif self.position and sell_check:
            self.order = self.order_target_percent(target=0)
            self.buy_sell_signals.append({"date": current_date,
                                          "signal": "SELL"})
        else:
            self.buy_sell_signals.append({"date": current_date,
                                          "signal": "WAIT"})

    def get_signals(self):
        # Returns the dates and signals as a list of dictionaries
        signals_data = []
        for signal in self.buy_sell_signals:
            date = signal["date"]
            signal_type = signal["signal"]

            signals_data.append({"date": date, "signal": signal_type})

        # Convert the list of dictionaries to a pandas DataFrame
        signals_df = pd.DataFrame(signals_data)

        return signals_df

    def stop(self):
        if False:
            string1 = str(self.params.hma_period) + " "
            string2 = str(self.params.atr_period) + " "
            string3 = str(self.params.buy_lag) + " "
            string4 = str(self.params.RangeStopLossMultiple) + " "
            string5 = str(self.params.ChannelStopLossMultiple) + " "
            string6 = str(self.params.DisasterStopLossMultiple) + " "
            string7 = str(self.broker.getvalue()) + " "
            log_string = string1 + string2 + string3
            + string4 + string5 + string6 + string7
            self.log(log_string, doprint=True)
