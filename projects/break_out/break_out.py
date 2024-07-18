import backtrader as bt
import pandas as pd


class HullATR(bt.Indicator):
    alias = ('HATR',)
    lines = ('hatr',)
    params = (
        ('period', 50),
        ('movav', bt.indicators.HullMovingAverage),
    )

    def __init__(self):
        tr = bt.indicators.TrueRange(self.data)
        self.lines.hatr = self.params.movav(tr, period=self.params.period)


class BreakOut(bt.Strategy):
    params = (
        ('printlog', False),
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

        # Buying Pattern Variables
        self.buyPatternComplete = False
        self.buyDelayComplete = False
        self.buyDaysCount = 0
        self.BuyLag = self.p.buy_lag

        # Sell Pattern Variables
        self.tradeHigh = 0.0
        self.stopLoss = 0.0
        self.RangeStopLossMultiple = self.p.RangeStopLossMultiple
        self.ChannelStopLossMultiple = self.p.ChannelStopLossMultiple
        self.DisasterStopLossMultiple = self.p.DisasterStopLossMultiple

        # Add a MovingAverageSimple indicator
        indicator_hma = bt.indicators.HullMovingAverage
        self.tr = bt.indicators.TR(self.data)
        self.atr = HullATR(self.data, period=self.p.atr_period)
        self.hullHigh = indicator_hma(self.data.high, period=self.p.hma_period)
        self.hullLow = indicator_hma(self.data.low, period=self.p.hma_period)

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

    def ResetPattern(self):
        self.buyPatternComplete = False
        self.buyDelayComplete = False
        self.buyDaysCount = 0

    def next(self):
        current_date = self.data.datetime.date()
        if self.buyPatternComplete:
            self.buyDaysCount = self.buyDaysCount + 1

        # Buy Check
        buyPattern1 = self.tr[0] > self.atr[0]
        buyPattern2 = self.data.close[0] > self.hullHigh[0]
        buyPattern3 = not self.buyPatternComplete
        buyCheck = buyPattern1 and buyPattern2 and buyPattern3

        if buyCheck:
            self.buyPatternComplete = True

        # Buy Delay
        buyDelay1 = self.buyPatternComplete and not self.buyDelayComplete
        buyDelay2 = self.buyDaysCount >= self.BuyLag

        buyDelay = buyDelay1 and buyDelay2

        # Sell Check
        stopLoss = self.data.high[0] > self.tradeHigh and self.position

        if (stopLoss):
            self.tradeHigh = self.data.high[0]
            self.stopLoss = (self.tradeHigh
                             - self.RangeStopLossMultiple * self.atr[0])

        if self.position:
            trailingStopLoss = self.data.close[0] < self.stopLoss
            priceChannelStopLoss = self.data.close[0] < (
                self.ChannelStopLossMultiple * self.hullLow[0])
            disasterStopLoss = self.data.close[0] < (
                self.buyprice * self.DisasterStopLossMultiple)

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        if not self.position:
            if self.buyPatternComplete and buyDelay:
                self.order_target_percent(target=0.95)
                self.buyprice = self.data.close[0]
                self.ResetPattern()
                self.buy_sell_signals.append({"date": current_date,
                                              "signal": "BUY",
                                              "tr": self.tr[0],
                                              "atr": self.atr[0],
                                              "close": self.data.close[0],
                                              "hull_high": self.hullHigh[0]})
            else:
                self.buy_sell_signals.append({"date": current_date,
                                              "signal": "WAIT",
                                              "tr": self.tr[0],
                                              "atr": self.atr[0],
                                              "close": self.data.close[0],
                                              "hull_high": self.hullHigh[0]})
        elif self.position and (trailingStopLoss
                                or priceChannelStopLoss
                                or disasterStopLoss):
            if trailingStopLoss:
                self.log('trailingStopLoss, %.2f' % self.dataclose[0])
            elif priceChannelStopLoss:
                self.log('priceChannelStopLoss, %.2f' % self.dataclose[0])
            else:
                self.log('disasterStopLoss, %.2f' % self.dataclose[0])
            self.order = self.order_target_percent(target=0.0)
            self.tradeHigh = 0.0
            self.stopLoss = 0.0
            self.buyprice = 0
            self.buy_sell_signals.append({"date": current_date,
                                          "signal": "SELL",
                                          "tr": self.tr[0],
                                          "atr": self.atr[0],
                                          "close": self.data.close[0],
                                          "hull_high": self.hullHigh[0]})
        else:
            self.buy_sell_signals.append({"date": current_date,
                                          "signal": "HOLD",
                                          "tr": self.tr[0],
                                          "atr": self.atr[0],
                                          "close": self.data.close[0],
                                          "hull_high": self.hullHigh[0]})
        self.log(current_date)

    def get_signals(self):
        # Returns the dates and signals as a list of dictionaries
        signals_data = []
        for signal in self.buy_sell_signals:
            date = signal["date"]
            signal_type = signal["signal"]
            tr_value = round(signal["tr"], 2)
            atr_value = round(signal["atr"], 2)
            close_value = round(signal["close"], 2)
            hh_value = round(signal["hull_high"], 2)

            signals_data.append({"date": date, "signal": signal_type,
                                 "tr": tr_value, "atr": atr_value,
                                 "close": close_value, "hull_high": hh_value})

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
