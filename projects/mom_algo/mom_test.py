import backtrader as bt
from projects.mom_algo.mom_algo import MomAlgo
# import numpy as np
import datetime

STRATEGY = MomAlgo
FROMDATE = datetime.datetime(2018, 1, 1)
# ODATE = datetime.datetime(2023, 4, 30)


def mom_opt(df):
    # DataFeed
    cash = 10000
    data_feed = bt.feeds.PandasData(dataname=df)
    # Initialize the Backtrader cerebro
    cerebro = bt.Cerebro(stdstats=True)
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=0.001)
    # Optimize
    if True:
        cerebro.optstrategy(
            STRATEGY,
            short_period=range(10, 22),
            long_period=range(15, 40)
            )
        cerebro.addanalyzer(bt.analyzers.Returns, _name='rtot')
    else:
        cerebro.addstrategy(STRATEGY)
    # Data
    cerebro.adddata(data_feed)

    # Run the optimization
    results = cerebro.run(maxcpus=1)

    final_results_list = []
    for run in results:
        for strategy in run:
            rtot = round(strategy.analyzers.rtot.get_analysis()['rtot'], 5)
            short_period = strategy.params.short_period
            long_period = strategy.params.long_period
            final_results_list.append([short_period, long_period, rtot])
    print(final_results_list)

    by_rtot = sorted(final_results_list, key=lambda x: x[2], reverse=False)

    # Print the top 5 strategies
    for res in by_rtot:
        print("Strategy: short_period={}, long_period={}, total return={}".format(*res))

    return True


def backtest_mom(df):
    cash = 1000
    data_feed = bt.feeds.PandasData(dataname=df,
                                    fromdate=FROMDATE)
    cerebro = bt.Cerebro(stdstats=True)
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addstrategy(STRATEGY)
    cerebro.adddata(data_feed)
    cerebro.addanalyzer(bt.analyzers.DrawDown)
    results = cerebro.run()
    strategy_instance = results[0]
    signals = strategy_instance.get_signals()
    drawdown_analyzer = results[0].analyzers.getbyname('drawdown')
    max_drawdown = drawdown_analyzer.get_analysis()['max']['drawdown']
    max_drawdown = round(max_drawdown, 1)
    performance = round(((cerebro.broker.getvalue() - cash) / cash) * 100, 1)

    return signals, performance, max_drawdown
