
## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/quanttrading-bot.git
    cd quanttrading-bot
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up environment variables by copying `.env.example` to `.env` and filling in the necessary details.

## Configuration

- **Strategies Configuration**: Define your strategies in the `config/strategies.yaml` file. Each strategy should have its parameters like `window` and `threshold`.

## Usage

1. Run the trading bot:
    ```sh
    python main.py
    ```

## Components

- **Data Fetcher**: Fetches market data from the exchange. Implemented in [`quanttrading.data_fetcher`](quanttrading/data_fetcher.py).
- **Strategies**: Contains the logic for different trading strategies. Implemented in [`quanttrading.strategies`](quanttrading/strategies.py).
- **Position Engine**: Calculates the position delta. Implemented in [`quanttrading.position_engine`](quanttrading/position_engine.py).
- **Trader**: Executes trades based on the calculated signals. Implemented in [`quanttrading.trader`](quanttrading/trader.py).
- **Logger**: Initializes and manages logging. Implemented in [`quanttrading.utils.log`](quanttrading/utils/log.py).
- **Config Manager**: Loads and manages configuration files. Implemented in [`quanttrading.config_manager`](quanttrading/config_manager.py).

## Strategies

### Strat01

A z-score momentum strategy that calculates the z-score of the closing prices and generates buy signals when the z-score exceeds a threshold.

### Strat02

A moving average percentage difference strategy that calculates the percentage difference between the closing price and its moving average, generating buy signals when the percentage difference exceeds a threshold.

## Data

- Historical data files are stored in the `data/` directory.
- Logs are stored in the `logs/` directory.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.