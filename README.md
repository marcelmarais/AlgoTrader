# AlgoTrader

**Welcome to AlgoTrader!**

AlgoTrader is a platform that automates technical analysis for stocks and their derivative instruments.

## Setup

Create a file called `apiKeys.txt` with your [News Api](https://newsapi.org/) key in the `/Data` directory. 

## Dependencies

Use pip to install dependencies from `requirements.txt`

```bash
pip install -r requirements.txt
```

## Options

When generating data with `generateTrainData.py` you have several options availible. These are all available as flags from the command line. 

| Flag | Name        | Description                                                                                             |
|------|-------------|---------------------------------------------------------------------------------------------------------|
| `-h` | Help        | Shows the help message.                                                                                 |
| `-t` | Ticker      | Specify the ticker symbol. A list is available [here](https://iextrading.com/trading/eligible-symbols/).|
| `-c` | Cache       | Use the previously generated data.                                                                      |
| `-s` | Sensitivity | Sets the buy/sell sensitivity for sentiment in STD multiples.                                           |
