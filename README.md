# Protogen - Algorithmic Trading Bot

A sophisticated algorithmic trading bot designed for cryptocurrency trading, specifically optimized for Bitcoin (BTC/USD) pairs. Protogen implements multiple trading strategies using technical indicators like Bollinger Bands, RSI, and Stochastic oscillators to make automated trading decisions.

## 🚀 Features

- **Multiple Trading Strategies**: Bollinger Bands + RSI strategy with customizable parameters
- **Paper Trading**: Test strategies without risking real money
- **Live Trading**: Execute real trades through Binance US exchange
- **Multi-Account Support**: Manage multiple trading accounts simultaneously
- **Backtesting Framework**: Comprehensive backtesting using Backtrader library
- **Strategy Optimization**: Parameter optimization using scipy optimization algorithms
- **Risk Management**: Built-in stop-loss and take-profit mechanisms
- **Real-time Data**: Live market data from Binance US

## 📁 Project Structure

```
Protogen/
├── strats/                          # Trading strategy implementations
│   ├── BBRSI.py                    # Bollinger Bands + RSI strategy
│   ├── MA600_cross.py              # 600-period MA crossover strategy
│   └── TradingStrat.py             # Base trading strategy class
├── backtesting/                     # Backtesting framework
│   ├── backtrader-test.py          # Main backtesting script
│   ├── BTStrats/                   # Backtrader strategy implementations
│   │   ├── BT_600MA_cross.py       # 600 MA crossover for Backtrader
│   │   ├── BT_SmaCross.py          # SMA crossover strategy
│   │   └── BT_buyandhold.py        # Buy and hold strategy
│   └── data/                       # Historical market data
│       └── BTC_5m/                 # 5-minute Bitcoin candle data
├── protogen_binanceUS_squad.py     # Multi-account live trading bot
├── protogen_paper_BBRSI.py         # Paper trading with BBRSI strategy
├── protogen_paper_BB.py            # Paper trading with Bollinger Bands
├── protogen_paper_BBRSI_backtest.py # Backtesting BBRSI strategy
├── backtest.py                     # General backtesting utilities
├── broker.py                       # Broker interface implementations
├── datastream.py                   # Data streaming utilities
└── gainslosses.py                  # P&L calculation utilities
```

## 🛠️ Installation

### Prerequisites

- Python 3.7+
- Binance US account (for live trading)
- API keys (for live trading)

### Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

Required packages:
- `ta` - Technical analysis library
- `schedule` - Task scheduling
- `ccxt` - Cryptocurrency exchange API
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `backtrader[plotting]` - Backtesting framework

## 🔧 Configuration

1. **API Keys Setup** (for live trading):
   Create a `config.py` file with your Binance US API credentials:
   ```python
   API_KEY = "your_binance_api_key"
   API_SECRET = "your_binance_secret_key"
   
   # For multi-account setup
   BUCHER_API_KEY = "account2_api_key"
   BUCHER_API_SECRET = "account2_secret_key"
   
   LEBER_API_KEY = "account3_api_key"
   LEBER_API_SECRET = "account3_secret_key"
   ```

2. **Strategy Parameters**:
   Customize trading parameters in the strategy files:
   - Risk/reward ratio
   - RSI thresholds
   - ATR multipliers
   - Bollinger Band sensitivity

## 🎯 Trading Strategies

### Bollinger Bands + RSI Strategy (BBRSI)

The main strategy combines multiple technical indicators:

- **Bollinger Bands**: Identifies overbought/oversold conditions
- **RSI (Relative Strength Index)**: Momentum oscillator
- **Stochastic RSI**: Additional momentum confirmation
- **ATR (Average True Range)**: Volatility-based stop losses

**Entry Signals**:
- **Long**: RSI oversold recovery + Stochastic crossover + Lower Bollinger Band touch
- **Short**: RSI overbought decline + Stochastic crossover + Upper Bollinger Band touch

**Exit Signals**:
- Stop-loss based on ATR
- Take-profit at risk/reward ratio targets
- Trailing stops for trend following

### Moving Average Crossover

- 600-period moving average crossover strategy
- Momentum-based entries with ATR-based stops

## 🚀 Usage

### Paper Trading

Start with paper trading to test strategies:

```bash
python protogen_paper_BBRSI.py
```

### Live Trading

⚠️ **Warning**: Live trading involves real money. Test thoroughly in paper mode first.

```bash
python protogen_binanceUS_squad.py
```

### Backtesting

Run historical backtests:

```bash
python protogen_paper_BBRSI_backtest.py
```

### Strategy Optimization

Optimize strategy parameters:

```bash
python protogen_paper_BBRSI_backtest_w-optimize.py
```

## 📊 Backtesting

The project includes comprehensive backtesting capabilities using both custom implementations and Backtrader:

### Custom Backtesting
- Historical data from 2020-2022
- 5-minute candle resolution
- Commission and slippage modeling
- Detailed trade logging

### Backtrader Integration
- Professional backtesting framework
- Multiple strategy comparison
- Performance metrics and plotting
- Portfolio analysis

## 🔍 Monitoring

The bot provides:
- Real-time position tracking
- P&L calculations
- Trade logging with timestamps
- Error handling and reconnection logic

## ⚠️ Risk Management

Built-in risk management features:
- **Position sizing**: Maximum 95% of available balance
- **Stop losses**: ATR-based dynamic stops
- **Take profits**: Risk/reward ratio targets
- **Trailing stops**: Protect profits in trending markets

## 📈 Performance Tracking

Track performance with:
- USD and BTC gains/losses
- Total return percentages
- Fee tracking
- Trade win/loss ratios

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test your changes thoroughly
4. Submit a pull request

## ⚠️ Disclaimer

**This software is for educational and research purposes only. Trading cryptocurrencies involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results. Use at your own risk.**

- Always test strategies in paper trading mode first
- Never invest more than you can afford to lose
- Ensure you understand the risks involved in algorithmic trading
- Market conditions can change rapidly and past performance may not be indicative of future results

## 📄 License

This project is open source. Please review the license terms before use.

## 🔗 Support

For questions or issues:
- Review the code documentation
- Check existing issues in the repository
- Test in paper trading mode before live deployment

---

**Happy Trading! 📈**