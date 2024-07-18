import backtrader as bt
from projects.algo_1.algo_1 import Algo
import datetime

STRATEGY = Algo
FROMDATE = datetime.datetime(2018, 1, 1)
# TODATE = datetime.datetime(2023, 9, 20)


def backtest_algo_1(df):
    data_feed = bt.feeds.PandasData(dataname=df,
                                    fromdate=FROMDATE)
    cerebro = bt.Cerebro(stdstats=True)
    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addstrategy(STRATEGY)
    cerebro.adddata(data_feed)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    results = cerebro.run()
    strategy_instance = results[0]
    signals = strategy_instance.get_signals()
    drawdown_analyzer = results[0].analyzers.getbyname('drawdown')
    drawdown = drawdown_analyzer.get_analysis()['drawdown']
    drawdown = round(drawdown, 1)
    performance = round(((cerebro.broker.getvalue() - 1000) / 1000) * 100, 1)

    return signals, performance, drawdown
