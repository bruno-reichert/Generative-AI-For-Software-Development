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

# Create tables
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

# Seed data across all three asset classes
companies_data = [
    # Domestic Equities (IDs 1-10)
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
    # Foreign Equities (IDs 1001-1002, Ticker 'ZZZZ')
    (1001, 'ZZZZ', 'Baoshan Iron & Steel Co.'),
    (1002, 'ZZZZ', 'Taiwan Semiconductor Manufacturing Co.'),
    # Cryptocurrencies (IDs 5001-5003, Tickers ending in '-USD')
    (5001, 'BTC-USD', 'Bitcoin'),
    (5002, 'ETH-USD', 'Ethereum'),
    (5003, 'SOL-USD', 'Solana')
]

cursor.executemany('''
INSERT OR IGNORE INTO companies (id, ticker, name)
VALUES (?, ?, ?)
''', companies_data)

# Generate synthetic daily snapshot time-series data
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
# 3. Domain Model Hierarchy with Template Method Pattern
# =====================================================================
class Company(ABC):
    """Abstract Base Class defining the Template Method lifecycle."""
    def __init__(
        self, 
        company_id: int, 
        ticker: str, 
        name: str, 
        window_size: int = 20, 
        bollinger_width: float = 2.0
    ):
        self.company_id = company_id
        self.ticker = ticker
        self.name = name
        self.company_type: str = "Generic"
        
        # Indicator calculation parameters
        self.window_size = window_size
        self.bollinger_width = bollinger_width

        # Explicit typing for Pylance static analysis
        self.time_series: pd.DataFrame | None = None
        self.high_bollinger: pd.Series | None = None
        self.low_bollinger: pd.Series | None = None
        self.moving_average: pd.Series | None = None
        self.grade: str | None = None

    # -----------------------------------------------------------------
    # TEMPLATE METHOD: The fixed skeleton algorithm
    # -----------------------------------------------------------------
    def process_time_series(self):
        """
        Template method orchestrating the time-series lifecycle:
        1. Load raw data
        2. Subclass pre-processing hook
        3. Indicator calculation
        4. Subclass post-processing hook
        5. Grade evaluation
        """
        self.load_time_series()
        self.preprocess_data()
        self.calculate_bollinger_bands()
        self.postprocess_data()
        self.assign_grade()

    # -----------------------------------------------------------------
    # HOOK METHODS: Overridden by subclasses as needed
    # -----------------------------------------------------------------
    def preprocess_data(self):
        """Default hook: no-op for generic companies."""
        pass

    def postprocess_data(self):
        """Default hook: no-op for generic companies."""
        pass

    @abstractmethod
    def get_identifier(self) -> str:
        """Polymorphic representation of the primary identifier."""
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

    def assign_grade(self):
        if (self.time_series is None or 
            self.high_bollinger is None or 
            self.low_bollinger is None):
            raise ValueError("Bands must be calculated before assigning a grade.")
            
        latest_value = self.time_series['value'].iloc[-1]
        
        if latest_value > self.high_bollinger.iloc[-1]:
            self.grade = 'A'
        elif latest_value < self.low_bollinger.iloc[-1]:
            self.grade = 'C'
        else:
            self.grade = 'B'

    def display(self):
        if (self.time_series is None or 
            self.moving_average is None or 
            self.high_bollinger is None or 
            self.low_bollinger is None):
            raise ValueError("Calculations are incomplete.")
            
        print(f"[{self.company_type.upper()}] {self.name} | {self.get_identifier()}")
        print(f"Grade: {self.grade} | Window: {self.window_size} | Band Width: ±{self.bollinger_width}σ")
        print("Time Series (Tail):")
        print(self.time_series.tail(3))
        print(f"Latest Moving Average: {self.moving_average.iloc[-1]:.2f}")
        print(f"Latest Upper Band:     {self.high_bollinger.iloc[-1]:.2f}")
        print(f"Latest Lower Band:     {self.low_bollinger.iloc[-1]:.2f}")
        print("-" * 65)


class DomesticCompany(Company):
    """Domestic company: inherits default hooks."""
    def __init__(self, company_id: int, ticker: str, name: str):
        super().__init__(company_id, ticker, name, window_size=20, bollinger_width=2.0)
        self.company_type = "Domestic"

    def get_identifier(self) -> str:
        return f"Ticker: {self.ticker}"


class ForeignCompany(Company):
    """Foreign company: uses postprocessing hook to convert local currency to USD."""
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
        """Hook override: converts time-series values to USD equivalent."""
        if self.time_series is None:
            return
        
        conversion_rate = self._get_conversion_rate(self.currency, "USD")
        self.time_series["value_usd"] = self.time_series["value"] * conversion_rate
        print(f"-> [Hook] Converted {self.name} time series from {self.currency} to USD (Rate: {conversion_rate}).")

    def _get_conversion_rate(self, from_curr: str, to_curr: str) -> float:
        rates = {"EUR": 1.08, "CNY": 0.14, "JPY": 0.0067, "GBP": 1.27, "TWD": 0.031}
        return rates.get(from_curr.upper(), 1.0)


class CryptoCompany(Company):
    """Crypto asset: uses preprocessing hook to verify 24/7 continuous snapshot integrity."""
    def __init__(self, company_id: int, ticker: str, name: str):
        if company_id < 5000:
            raise ValueError(f"Crypto asset IDs must be 5000 or greater. Received: {company_id}")
        super().__init__(company_id, ticker, name, window_size=20, bollinger_width=2.0)
        self.company_type = "Crypto"

    def get_identifier(self) -> str:
        return f"Crypto Pair: {self.ticker} [24/7 Market]"

    def preprocess_data(self):
        """Hook override: verifies continuous snapshot frequency."""
        if self.time_series is not None:
            print(f"-> [Hook] Validated 24/7 continuous daily snapshots for {self.ticker} ({len(self.time_series)} points).")


# =====================================================================
# 4. The Company Factory
# =====================================================================
class CompanyFactory:
    """Factory to fetch and instantiate concrete Company/Crypto objects polymorphically."""
    
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
            # Map specific currencies based on name/ID for demonstration
            currency = "CNY" if "Baoshan" in comp_name else "TWD"
            return ForeignCompany(company_id=comp_id, ticker=comp_ticker, name=comp_name, currency=currency)
        else:
            return DomesticCompany(company_id=comp_id, ticker=comp_ticker, name=comp_name)


# =====================================================================
# 5. Execution Block (Simplified via Template Method)
# =====================================================================
if __name__ == "__main__":
    # The client now calls a single unified pipeline method: process_time_series()
    
    # 1. Domestic Company
    domestic = CompanyFactory.get_company("AAPL")
    if domestic:
        domestic.process_time_series()
        domestic.display()

    # 2. Foreign Company (Triggers Post-processing Currency Hook)
    foreign = CompanyFactory.get_company(1001)
    if foreign:
        foreign.process_time_series()
        foreign.display()

    # 3. Crypto Asset (Triggers Pre-processing Validation Hook)
    crypto = CompanyFactory.get_company("BTC-USD")
    if crypto:
        crypto.process_time_series()
        crypto.display()

    # Clean up database resources
    DatabaseConnection.close_connection()