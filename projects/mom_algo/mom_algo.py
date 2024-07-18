import backtrader as bt
import pandas as pd


class MomAlgo(bt.Strategy):
    params = (('short_period', 11), ('long_period', 78), ('stop_loss', 0.04))

    def __init__(self):
        self.data_close = self.datas[0].close
        self.buy_sell_signals = []

        # Momentum indicator
        self.short_mom = bt.indicators.Momentum(
            self.data.close, period=self.params.short_period)
        self.long_mom = bt.indicators.Momentum(
            self.data.close, period=self.params.long_period)

        # CrossOver Signal
        self.crossover = bt.indicators.CrossOver(self.short_mom, self.long_mom)

    def next(self):
        buy_check1 = self.crossover > 0

        # print(self.short_mom[0])
        # print(self.crossover[0])

        if not self.position:  # not in the market
            if (buy_check1):
                self.buy()  # enter long
                self.buy_sell_signals.append(
                    {"date": self.data.datetime.date(0), "signal": "BUY"})
                # Set stop loss
                stop_price = self.data.close[0] * (1 - self.params.stop_loss)
                self.sell(exectype=bt.Order.Stop, price=stop_price)
        elif self.position and self.crossover < 0:
            self.close()  # close long position
            self.buy_sell_signals.append(
                {"date": self.data.datetime.date(0), "signal": "SELL"})

    def get_signals(self):
        signals_data = self.buy_sell_signals
        signals_df = pd.DataFrame(signals_data)
        return signals_df
