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

# Seed data across all three asset classes:
# 1-999: Domestic Equities | 1000-4999: Foreign Equities | 5000+: Crypto Assets
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
    # Scale synthetic price range per asset class
    if company_id >= 5000:
        base_low, base_high = 1000, 30000  # Crypto scale
    else:
        base_low, base_high = 50, 600      # Traditional equity scale

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
# 3. Domain Model Hierarchy (Polymorphism)
# =====================================================================
class Company(ABC):
    """Abstract Base Class for all financial entities."""
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
        
        # Indicator calculation parameters (configurable per subclass)
        self.window_size = window_size
        self.bollinger_width = bollinger_width

        # Explicit typing for Pylance static analysis
        self.time_series: pd.DataFrame | None = None
        self.high_bollinger: pd.Series | None = None
        self.low_bollinger: pd.Series | None = None
        self.moving_average: pd.Series | None = None
        self.grade: str | None = None

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
        print(f"Grade: {self.grade} | Window: {self.window_size} periods | Band Width: ±{self.bollinger_width}σ")
        print("Time Series (Tail):")
        print(self.time_series.tail(3))
        print(f"Latest Moving Average: {self.moving_average.iloc[-1]:.2f}")
        print(f"Latest Upper Band:     {self.high_bollinger.iloc[-1]:.2f}")
        print(f"Latest Lower Band:     {self.low_bollinger.iloc[-1]:.2f}")
        print("-" * 65)


class DomesticCompany(Company):
    """Domestic company identified primarily by its unique stock ticker."""
    def __init__(self, company_id: int, ticker: str, name: str):
        super().__init__(company_id, ticker, name, window_size=20, bollinger_width=2.0)
        self.company_type = "Domestic"

    def get_identifier(self) -> str:
        return f"Ticker: {self.ticker}"


class ForeignCompany(Company):
    """Foreign company identified primarily by a 4-digit ID with standard 'ZZZZ' ticker."""
    FOREIGN_TICKER = "ZZZZ"

    def __init__(self, company_id: int, ticker: str, name: str):
        if not (1000 <= company_id <= 4999):
            raise ValueError(f"Foreign company IDs must be between 1000 and 4999. Received: {company_id}")
        super().__init__(company_id, ticker, name, window_size=20, bollinger_width=2.0)
        self.company_type = "Foreign"

    def get_identifier(self) -> str:
        return f"Foreign ID: {self.company_id} (Placeholder Ticker: {self.ticker})"


class CryptoCompany(Company):
    """Cryptocurrency asset trading 24/7, tracked via midnight UTC daily snapshots."""
    def __init__(self, company_id: int, ticker: str, name: str):
        if company_id < 5000:
            raise ValueError(f"Crypto asset IDs must be 5000 or greater. Received: {company_id}")
        # Crypto configured with standard 20 daily snapshots and 2.0 sigma width
        super().__init__(company_id, ticker, name, window_size=20, bollinger_width=2.0)
        self.company_type = "Crypto"

    def get_identifier(self) -> str:
        return f"Crypto Pair: {self.ticker} [24/7 Market - Midnight UTC Snapshot]"


# =====================================================================
# 4. The Company Factory
# =====================================================================
class CompanyFactory:
    """Factory to fetch and instantiate concrete Company/Crypto objects polymorphically."""
    
    FOREIGN_TICKER = "ZZZZ"

    @classmethod
    def get_company(cls, identifier: int | str) -> Company | None:
        """
        Unified factory method.
        - String identifier: queries by ticker (Domestic, Foreign, or Crypto pair).
        - Integer identifier: queries by ID across all ID ranges.
        """
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

        # Creational Decision Tree
        if comp_id >= 5000 or comp_ticker.endswith("-USD"):
            return CryptoCompany(company_id=comp_id, ticker=comp_ticker, name=comp_name)
        elif comp_id >= 1000 or comp_ticker == cls.FOREIGN_TICKER:
            return ForeignCompany(company_id=comp_id, ticker=comp_ticker, name=comp_name)
        else:
            return DomesticCompany(company_id=comp_id, ticker=comp_ticker, name=comp_name)


# =====================================================================
# 5. Execution Block
# =====================================================================
if __name__ == "__main__":
    # Test 1: Fetch Domestic Company by Ticker
    domestic = CompanyFactory.get_company("AAPL")
    if domestic:
        domestic.load_time_series()
        domestic.calculate_bollinger_bands()
        domestic.assign_grade()
        domestic.display()

    # Test 2: Fetch Foreign Company by ID
    foreign = CompanyFactory.get_company(1001)
    if foreign:
        foreign.load_time_series()
        foreign.calculate_bollinger_bands()
        foreign.assign_grade()
        foreign.display()

    # Test 3: Fetch Crypto Asset by Ticker Pair
    btc = CompanyFactory.get_company("BTC-USD")
    if btc:
        btc.load_time_series()
        btc.calculate_bollinger_bands()
        btc.assign_grade()
        btc.display()

    # Test 4: Fetch Crypto Asset by 5000+ ID
    eth = CompanyFactory.get_company(5002)
    if eth:
        eth.load_time_series()
        eth.calculate_bollinger_bands()
        eth.assign_grade()
        eth.display()

    # Test 5: Verify Company Types dynamically
    for test_id in [1, 1001, 5001]:
        entity = CompanyFactory.get_company(test_id)
        if entity:
            print(f"Verified {entity.name} -> Class: {type(entity).__name__}, Type: {entity.company_type}")

    # Safely close database connection
    DatabaseConnection.close_connection()