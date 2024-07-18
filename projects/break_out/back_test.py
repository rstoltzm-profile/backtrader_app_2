import backtrader as bt
from projects.break_out.break_out import BreakOut
import numpy as np
import datetime

STRATEGY = BreakOut
FROMDATE = datetime.datetime(2018, 1, 1)
# ODATE = datetime.datetime(2023, 4, 30)


def backtest_optimizer(df):
    # DataFeed
    data_feed = bt.feeds.PandasData(dataname=df)
    # Initialize the Backtrader cerebro
    cerebro = bt.Cerebro(stdstats=False)
    cerebro.broker.setcash(1000)
    cerebro.broker.setcommission(commission=0.001)
    # Optimize
    if False:
        cerebro.optstrategy(STRATEGY,
                            DisasterStopLossMultiple=np.arange(0.85, 1.0, .02),
                            RangeStopLossMultiple=np.arange(1.5, 3.5, 0.2))
        # cerebro.optstrategy(BreakOut, buy_lag = range(2,8))
        cerebro.addanalyzer(bt.analyzers.Returns, _name='rtot')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    else:
        cerebro.addstrategy(STRATEGY)
    # Data
    cerebro.adddata(data_feed)

    # Run the optimization

    results = cerebro.run(maxcpus=1)
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    results = 100 * ((cerebro.broker.getvalue() - 10000) / 10000)
    print(results)

    if False:
        # Find the best parameter combination
        best_drawdown = None
        best_params = None
        best_rtot = None

        for res in results:
            for strategy in res:
                analyzers = strategy.analyzers
                drawdown = analyzers.get_analysis()['drawdown']
                rtot = strategy.analyzers.rtot.get_analysis()['rtot']
                if best_rtot is None or rtot > best_rtot:
                    best_drawdown = drawdown
                    best_params = strategy.params
                    best_rtot = rtot

        print("Best Parameters:")
        print("Best DisasterStopLossMultiple",
              best_params.DisasterStopLossMultiple)
        print("RangeStopLossMultiple", best_params.RangeStopLossMultiple)
        print("Best Total Return:", best_rtot)
        print("Best Drawdown:", best_drawdown)


def backtest_break_out(df):
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
    max_drawdown = drawdown_analyzer.get_analysis()['max']['drawdown']
    max_drawdown = round(max_drawdown, 1)
    performance = round(((cerebro.broker.getvalue() - 1000) / 1000) * 100, 1)

    return signals, performance, max_drawdown
