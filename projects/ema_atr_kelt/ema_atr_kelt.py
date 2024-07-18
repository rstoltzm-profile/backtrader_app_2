import backtrader as bt
import pandas as pd


class EmaAtrKelt(bt.Strategy):
    params = (
        ('ema_period', 20),
        ('atr_period', 14),
        ('keltner_dev', 2.24),
        ('stop_atr', 1.4),
        ('rsi_period', 14),  # RSI period
        ('rsi_lower', 30),  # Lower threshold for oversold conditions
        ('rsi_upper', 70),  # Upper threshold for overbought conditions
    )

    def __init__(self):
        self.keltner_dev = float(self.params.keltner_dev)
        self.stop_atr = float(self.params.stop_atr)
        self.buy_sell_signals = []
        self.ema = bt.indicators.EMA(self.data.close,
                                     period=self.params.ema_period)
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)
        self.keltner_top = self.ema + self.keltner_dev * self.atr
        self.keltner_bot = self.ema - self.keltner_dev * self.atr
        self.rsi = bt.indicators.RSI(self.data.close,
                                     period=self.params.rsi_period)  # RSI indicator
        self.order = None

    def next(self):
        if not self.position:  # not in the market
            if self.data.close[0] <= self.keltner_bot[0] and self.rsi < self.params.rsi_lower:  # if the price is oversold and RSI is below lower threshold
                self.order = self.buy()  # enter a long position
                stop_price = self.data.close[0] - self.stop_atr * self.atr[0]
                self.sell(exectype=bt.Order.Stop, price=stop_price)  # set a stop loss order

        else:  # in the market
            if self.data.close[0] >= self.keltner_top[0] or self.rsi > self.params.rsi_upper:  # if the price is overbought and RSI is above upper threshold
                self.order = self.close()  # exit the long position

    def get_signals(self):
        signals_data = self.buy_sell_signals
        signals_df = pd.DataFrame(signals_data)
        return signals_df
