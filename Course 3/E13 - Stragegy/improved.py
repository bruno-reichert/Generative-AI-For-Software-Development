from __future__ import annotations
import random
import sqlite3
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import pandas as pd

# =====================================================================
# 1. Singleton Database Connection Class
# =====================================================================
class DatabaseConnection:
    """
    An optimized, thread-safe, and configurable Singleton class 
    to manage a single database connection.
    """
    _instance = None
    _lock = threading.Lock()
    connection: sqlite3.Connection

    def __new__(cls, db_path: str):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance.connection = sqlite3.connect(db_path)
        return cls._instance

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        if cls._instance is None:
            raise RuntimeError(
                "DatabaseConnection has not been initialized. "
                "Call DatabaseConnection('path_to_db.db') first."
            )
        return cls._instance.connection

    @classmethod
    def close_connection(cls):
        if cls._instance:
            with cls._lock:
                if cls._instance:
                    cls._instance.connection.close()
                    cls._instance = None


# =====================================================================
# 2. Database Schema Creation and Seeding
# =====================================================================
DatabaseConnection('company_database.db')
conn = DatabaseConnection.get_connection()
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    name TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS TimeSeries (
    id INTEGER PRIMARY KEY,
    company_id INTEGER,
    value REAL,
    date TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id)
)
''')

# Seed all 3 asset classes: Domestic (1-999), Foreign (1000-4999), Crypto (5000+)
companies_data = [
    # Domestic Equities
    (1, 'AAPL', 'Apple Inc.'),
    (2, 'GOOGL', 'Alphabet Inc.'),
    (3, 'MSFT', 'Microsoft Corporation'),
    (4, 'AMZN', 'Amazon.com Inc.'),
    (5, 'TSLA', 'Tesla Inc.'),
    (6, 'META', 'Meta Platforms Inc.'),
    (7, 'NVDA', 'NVIDIA Corporation'),
    (8, 'NFLX', 'Netflix Inc.'),
    (9, 'ADBE', 'Adobe Inc.'),
    (10, 'ORCL', 'Oracle Corporation'),
    # Foreign Equities (Placeholder Ticker 'ZZZZ')
    (1001, 'ZZZZ', 'Baoshan Iron & Steel Co.'),
    (1002, 'ZZZZ', 'Taiwan Semiconductor Manufacturing Co.'),
    # Cryptocurrencies (Tickers ending in '-USD' or starting with 'X')
    (5001, 'BTC-USD', 'Bitcoin'),
    (5002, 'ETH-USD', 'Ethereum'),
    (5003, 'SOL-USD', 'Solana')
]

cursor.executemany('''
INSERT OR IGNORE INTO companies (id, ticker, name)
VALUES (?, ?, ?)
''', companies_data)

# Generate synthetic daily snapshot time series
start_date = datetime(2023, 1, 1)
num_entries = 100
time_series_data = []

for company in companies_data:
    company_id = company[0]
    base_low, base_high = (1000, 30000) if company_id >= 5000 else (50, 600)

    for i in range(num_entries):
        date = start_date + timedelta(days=i)
        value = round(random.uniform(base_low, base_high), 2)
        time_series_data.append((company_id, value, date.strftime('%Y-%m-%d')))

cursor.executemany('''
INSERT OR IGNORE INTO TimeSeries (company_id, value, date)
VALUES (?, ?, ?)
''', time_series_data)

conn.commit()


# =====================================================================
# 3. Strategy Pattern: Grading Algorithms
# =====================================================================
class GradingStrategy(ABC):
    """Abstract Strategy interface for assigning grades to financial entities."""
    @abstractmethod
    def assign_grade(self, company: Company) -> str:
        pass


class BollingerBandGradingStrategy(GradingStrategy):
    """Assigns grades based on position relative to upper and lower Bollinger Bands."""
    def assign_grade(self, company: Company) -> str:
        if (company.time_series is None or 
            company.high_bollinger is None or 
            company.low_bollinger is None):
            raise ValueError("Time series and Bollinger Bands must be calculated first.")

        latest_value = company.time_series['value'].iloc[-1]
        
        if latest_value > company.high_bollinger.iloc[-1]:
            return 'A'
        elif latest_value < company.low_bollinger.iloc[-1]:
            return 'C'
        else:
            return 'B'


class ThresholdGradingStrategy(GradingStrategy):
    """Assigns grades based on absolute price thresholds."""
    def __init__(self, high_threshold: float = 200.0, low_threshold: float = 100.0):
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold

    def assign_grade(self, company: Company) -> str:
        if company.time_series is None:
            raise ValueError("Time series must be loaded before assigning a threshold grade.")

        latest_value = company.time_series['value'].iloc[-1]
        
        if latest_value > self.high_threshold:
            return 'A'
        elif latest_value < self.low_threshold:
            return 'C'
        else:
            return 'B'


# =====================================================================
# 4. Domain Model Hierarchy (Template Method Pattern)
# =====================================================================
class Company(ABC):
    """Abstract Base Class defining the Template Method lifecycle."""
    def __init__(
        self, 
        company_id: int, 
        ticker: str, 
        name: str, 
        window_size: int = 20, 
        bollinger_width: float = 2.0,
        default_strategy: GradingStrategy | None = None
    ):
        self.company_id = company_id
        self.ticker = ticker
        self.name = name
        self.company_type: str = "Generic"
        
        # Indicator calculation parameters
        self.window_size = window_size
        self.bollinger_width = bollinger_width
        self.grading_strategy: GradingStrategy = default_strategy or BollingerBandGradingStrategy()

        # Explicit typing for Pylance static analysis
        self.time_series: pd.DataFrame | None = None
        self.high_bollinger: pd.Series | None = None
        self.low_bollinger: pd.Series | None = None
        self.moving_average: pd.Series | None = None
        self.grade: str | None = None

    # -----------------------------------------------------------------
    # TEMPLATE METHOD
    # -----------------------------------------------------------------
    def process_time_series(self, strategy: GradingStrategy | None = None):
        """Standardized lifecycle pipeline utilizing interchangeable strategies."""
        self.load_time_series()
        self.preprocess_data()
        self.calculate_bollinger_bands()
        self.postprocess_data()
        self.assign_grade(strategy or self.grading_strategy)

    # -----------------------------------------------------------------
    # HOOK METHODS
    # -----------------------------------------------------------------
    def preprocess_data(self):
        pass

    def postprocess_data(self):
        pass

    @abstractmethod
    def get_identifier(self) -> str:
        pass

    def load_time_series(self):
        conn = DatabaseConnection.get_connection()
        query = '''
        SELECT date, value
        FROM TimeSeries
        WHERE company_id = ?
        ORDER BY date
        '''
        self.time_series = pd.read_sql_query(query, conn, params=(self.company_id,))
        self.time_series['date'] = pd.to_datetime(self.time_series['date'])

    def calculate_bollinger_bands(self):
        if self.time_series is None:
            raise ValueError("Time series must be loaded before calculating bands.")
            
        rolling_mean = self.time_series['value'].rolling(self.window_size).mean()
        rolling_std = self.time_series['value'].rolling(self.window_size).std()
        
        self.moving_average = rolling_mean
        self.high_bollinger = rolling_mean + (rolling_std * self.bollinger_width)
        self.low_bollinger = rolling_mean - (rolling_std * self.bollinger_width)

    def assign_grade(self, strategy: GradingStrategy):
        """Delegates grading calculation to the injected strategy."""
        self.grade = strategy.assign_grade(self)

    def display(self):
        if (self.time_series is None or 
            self.moving_average is None or 
            self.high_bollinger is None or 
            self.low_bollinger is None):
            raise ValueError("Calculations are incomplete.")
            
        print(f"[{self.company_type.upper()}] {self.name} | {self.get_identifier()}")
        print(f"Grade: {self.grade} (Strategy: {type(self.grading_strategy).__name__})")
        print(f"Window: {self.window_size} periods | Band Width: ±{self.bollinger_width}σ")
        print("Time Series (Tail):")
        print(self.time_series.tail(3))
        print(f"Latest Value:          {self.time_series['value'].iloc[-1]:.2f}")
        print(f"Latest Moving Average: {self.moving_average.iloc[-1]:.2f}")
        print(f"Latest Upper Band:     {self.high_bollinger.iloc[-1]:.2f}")
        print(f"Latest Lower Band:     {self.low_bollinger.iloc[-1]:.2f}")
        print("-" * 65)


class DomesticCompany(Company):
    def __init__(self, company_id: int, ticker: str, name: str):
        super().__init__(company_id, ticker, name, window_size=20, bollinger_width=2.0)
        self.company_type = "Domestic"

    def get_identifier(self) -> str:
        return f"Ticker: {self.ticker}"


class ForeignCompany(Company):
    FOREIGN_TICKER = "ZZZZ"

    def __init__(self, company_id: int, ticker: str, name: str, currency: str = "EUR"):
        if not (1000 <= company_id <= 4999):
            raise ValueError(f"Foreign company IDs must be between 1000 and 4999. Received: {company_id}")
        super().__init__(company_id, ticker, name, window_size=20, bollinger_width=2.0)
        self.company_type = "Foreign"
        self.currency = currency

    def get_identifier(self) -> str:
        return f"Foreign ID: {self.company_id} (Currency: {self.currency})"

    def postprocess_data(self):
        if self.time_series is None:
            return
        rate = self._get_conversion_rate(self.currency, "USD")
        self.time_series["value_usd"] = self.time_series["value"] * rate
        print(f"-> [Hook] Converted {self.name} from {self.currency} to USD (Rate: {rate}).")

    def _get_conversion_rate(self, from_curr: str, to_curr: str) -> float:
        rates = {"EUR": 1.08, "CNY": 0.14, "JPY": 0.0067, "GBP": 1.27, "TWD": 0.031}
        return rates.get(from_curr.upper(), 1.0)


class CryptoCompany(Company):
    def __init__(self, company_id: int, ticker: str, name: str):
        if company_id < 5000:
            raise ValueError(f"Crypto asset IDs must be 5000 or greater. Received: {company_id}")
        super().__init__(company_id, ticker, name, window_size=20, bollinger_width=2.0)
        self.company_type = "Crypto"

    def get_identifier(self) -> str:
        return f"Crypto Pair: {self.ticker} [24/7 Market]"

    def preprocess_data(self):
        if self.time_series is not None:
            print(f"-> [Hook] Validated 24/7 daily snapshots for {self.ticker} ({len(self.time_series)} points).")


# =====================================================================
# 5. Factory Pattern
# =====================================================================
class CompanyFactory:
    FOREIGN_TICKER = "ZZZZ"

    @classmethod
    def get_company(cls, identifier: int | str) -> Company | None:
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        if isinstance(identifier, str):
            query = "SELECT id, ticker, name FROM companies WHERE ticker = ?"
            cursor.execute(query, (identifier,))
        else:
            query = "SELECT id, ticker, name FROM companies WHERE id = ?"
            cursor.execute(query, (identifier,))

        row = cursor.fetchone()
        if not row:
            return None

        comp_id, comp_ticker, comp_name = row[0], row[1], row[2]

        if comp_id >= 5000 or comp_ticker.endswith("-USD") or comp_ticker.startswith("X"):
            return CryptoCompany(company_id=comp_id, ticker=comp_ticker, name=comp_name)
        elif comp_id >= 1000 or comp_ticker == cls.FOREIGN_TICKER:
            currency = "CNY" if "Baoshan" in comp_name else "TWD"
            return ForeignCompany(company_id=comp_id, ticker=comp_ticker, name=comp_name, currency=currency)
        else:
            return DomesticCompany(company_id=comp_id, ticker=comp_ticker, name=comp_name)


# =====================================================================
# 6. Execution Block: Testing Dynamic Strategy Swapping
# =====================================================================
if __name__ == "__main__":
    # 1. Evaluate Apple with the default Bollinger Bands Strategy
    apple = CompanyFactory.get_company("AAPL")
    if apple:
        apple.process_time_series()
        apple.display()

        # Dynamically switch Apple to Threshold Grading Strategy at runtime
        threshold_strat = ThresholdGradingStrategy(high_threshold=400.0, low_threshold=150.0)
        apple.assign_grade(threshold_strat)
        print(f"==> Apple re-evaluated with Threshold Strategy (High>400, Low<150): Grade = {apple.grade}\n")

    # 2. Evaluate Foreign Company
    baoshan = CompanyFactory.get_company(1001)
    if baoshan:
        baoshan.process_time_series()
        baoshan.display()

    # 3. Evaluate Crypto Company
    btc = CompanyFactory.get_company("BTC-USD")
    if btc:
        btc.process_time_series()
        btc.display()

    DatabaseConnection.close_connection()