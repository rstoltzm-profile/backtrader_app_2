import backtrader as bt
from projects.buy_hold.buy_hold import BuyHold
import datetime

STRATEGY = BuyHold
FROMDATE = datetime.datetime(2016, 1, 1)


def backtest_buy_hold(df):
    data_feed = bt.feeds.PandasData(dataname=df,
                                    fromdate=FROMDATE)
    cerebro = bt.Cerebro(stdstats=True)
    cash = 10000
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addstrategy(STRATEGY)
    cerebro.adddata(data_feed)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    results = cerebro.run()
    drawdown_analyzer = results[0].analyzers.getbyname('drawdown')
    max_drawdown = drawdown_analyzer.get_analysis()['max']['drawdown']
    max_drawdown = round(max_drawdown, 1)
    performance = round(((cerebro.broker.getvalue() - cash) / cash) * 100, 1)

    return performance, max_drawdown
