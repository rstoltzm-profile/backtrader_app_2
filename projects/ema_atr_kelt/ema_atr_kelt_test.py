import backtrader as bt
from projects.ema_atr_kelt.ema_atr_kelt import DmaStrategy
import numpy as np
import datetime

STRATEGY = DmaStrategy
FROMDATE = datetime.datetime(2018, 1, 1)
# ODATE = datetime.datetime(2023, 4, 30)


def opt_ema_atr_kelt(df):
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
            # ema_period=range(150, 200, 5),
            ema_period=160,
            # atr_period=range(80, 100, 5),
            atr_period=90,
            keltner_dev=2.24,
            # keltner_dev=np.arange(2.2, 2.3, 0.01),
            stop_atr=1.4
            # stop_atr=np.arange(1.3, 1.5, 0.01)
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
            ema_period = strategy.params.ema_period
            atr_period = strategy.params.atr_period
            keltner_dev = round(strategy.params.keltner_dev, 2)
            stop_atr = round(strategy.params.stop_atr, 2)
            final_results_list.append(
                [ema_period, atr_period, keltner_dev, stop_atr, rtot])
    print(final_results_list)

    by_rtot = sorted(final_results_list, key=lambda x: x[4], reverse=False)

    for res in by_rtot:
        print(res)

    return True


def backtest_ema_atr_kelt(df):
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
    print(performance)
    return signals, performance, max_drawdown
