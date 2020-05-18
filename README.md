# Trading Bot Simulator
-----

This is the repository for all of the bot code. Once launched, it will wait till market opens and start intra-day trading on a selection of NYSE-listed stocks.
Buying and selling decisions are based on the supports and resistances found over last year's price curve.

## Installation of libraries
You'll need Python 3 installed with pip. Here is a non-exhaustive list of dependencies you might want to install:
```bash
pip install yfinance
pip install alpha_vantage

pip install tqdm
pip install datetime
pip install pytz
pip install calendar
pip install holidays

pip install requests
pip install string
pip install trendln
pip install email
pip install smtplib
pip install ssl
```

## Running the code
Preliminary steps:
- Data is real-time retrieved using a [python wrapper](https://github.com/RomelTorres/alpha_vantage) for [AlphaVantage API](https://www.alphavantage.co). Before running anything, you must [claim your API key](https://www.alphavantage.co/support/#api-key) on their website.

- Everytime the bot performs a trade, you will receive an e-mail at a specified address.

On your Command Line, make sure the working directory is correctly assigned, and run: `python3 main.py`. You will then be asked for your API key and the e-mail address where you want to receive updates.

## Roadmap
Ideas for future releases:
- Finding new stocks for which we can freely retrieve real-time data points, and adding them to the list of candidates
- Improving the stocks selection method at the beginning of each trading day
- Complexifying the trading strategy, by considering meaningful technical indicators. Ex: Moving Averages (SMA/EMA) to detect trends + Relative Strength Index (RSI) along with Commodity Channel Index (CCI) and other momentum oscillators to look for possible price breakouts.

## Support
If you have any questions or need help, feel free to get in touch at gforto97@hotmail.com. All contribution ideas are welcomed.
