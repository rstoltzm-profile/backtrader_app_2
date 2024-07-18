import backtrader as bt
from projects.buy_sell.buy_sell import BuySell
import datetime

STRATEGY = BuySell
FROMDATE = datetime.datetime(2021, 1, 1)
TODATE = datetime.datetime(2023, 4, 30)


def backtest_buy_sell(df):
    data_feed = bt.feeds.PandasData(dataname=df,
                                    fromdate=FROMDATE,
                                    todate=TODATE)
    cerebro = bt.Cerebro(stdstats=True)
    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addstrategy(STRATEGY)
    cerebro.adddata(data_feed)
    cerebro.run()
    cerebro.plot()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
