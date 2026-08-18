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
# Initialize singleton connection
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

# Seed domestic companies (IDs 1-10) and foreign companies (4-digit IDs with 'ZZZZ' ticker)
companies_data = [
    # Domestic
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
    # Foreign (Placeholder ticker 'ZZZZ', 4-digit IDs)
    (1001, 'ZZZZ', 'Baoshan Iron & Steel Co.'),
    (1002, 'ZZZZ', 'Taiwan Semiconductor Manufacturing Co.')
]

cursor.executemany('''
INSERT OR IGNORE INTO companies (id, ticker, name)
VALUES (?, ?, ?)
''', companies_data)

# Generate synthetic time-series data
start_date = datetime(2023, 1, 1)
num_entries = 100
time_series_data = []

for company in companies_data:
    company_id = company[0]
    for i in range(num_entries):
        date = start_date + timedelta(days=i)
        value = round(random.uniform(50, 600), 2)
        time_series_data.append((company_id, value, date.strftime('%Y-%m-%d')))

cursor.executemany('''
INSERT OR IGNORE INTO TimeSeries (company_id, value, date)
VALUES (?, ?, ?)
''', time_series_data)

conn.commit()

# Calculation constants
BOLLINGER_WIDTH = 2
WINDOW_SIZE = 20


# =====================================================================
# 3. Domain Model Hierarchy (Polymorphism)
# =====================================================================
class Company(ABC):
    """Abstract Base Class for all company entities."""
    def __init__(self, company_id: int, ticker: str, name: str):
        self.company_id = company_id
        self.ticker = ticker
        self.name = name
        
        # Pylance-safe explicit type hints
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
            
        rolling_mean = self.time_series['value'].rolling(WINDOW_SIZE).mean()
        rolling_std = self.time_series['value'].rolling(WINDOW_SIZE).std()
        
        self.moving_average = rolling_mean
        self.high_bollinger = rolling_mean + (rolling_std * BOLLINGER_WIDTH)
        self.low_bollinger = rolling_mean - (rolling_std * BOLLINGER_WIDTH)

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
            
        print(f"Company: {self.name} [{self.get_identifier()}]")
        print(f"Grade: {self.grade}")
        print("Time Series (Tail):")
        print(self.time_series.tail(3))
        print(f"Latest Moving Average: {self.moving_average.iloc[-1]:.2f}")
        print(f"Latest Upper Band: {self.high_bollinger.iloc[-1]:.2f}")
        print(f"Latest Lower Band: {self.low_bollinger.iloc[-1]:.2f}")
        print("-" * 50)


class DomesticCompany(Company):
    def __init__(self, company_id: int, ticker: str, name: str):
        super().__init__(company_id, ticker, name)
        self.company_type = "Domestic"

    def get_identifier(self) -> str:
        return f"Domestic Ticker: {self.ticker}"


class ForeignCompany(Company):
    def __init__(self, company_id: int, ticker: str, name: str):
        if not (1000 <= company_id <= 9999):
            raise ValueError(f"Foreign company IDs must be 4-digit integers. Received: {company_id}")
        super().__init__(company_id, ticker, name)
        self.company_type = "Foreign"

    def get_identifier(self) -> str:
        return f"Foreign ID: {self.company_id} (Ticker: {self.ticker})"


# =====================================================================
# 4. The Company Factory
# =====================================================================
class CompanyFactory:
    """Factory to fetch and instantiate concrete Company objects polymorphically."""
    
    FOREIGN_TICKER = "ZZZZ"

    @classmethod
    def get_company(cls, identifier: int | str) -> Company | None:
        """
        Unified factory method.
        - String identifier: queries by ticker and returns DomesticCompany.
        - Integer identifier: queries by ID, checking if it is Foreign or Domestic.
        """
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()

        if isinstance(identifier, str):
            query = "SELECT id, ticker, name FROM companies WHERE ticker = ?"
            cursor.execute(query, (identifier,))
            row = cursor.fetchone()
            if row:
                return DomesticCompany(company_id=row[0], ticker=row[1], name=row[2])
        else:
            query = "SELECT id, ticker, name FROM companies WHERE id = ?"
            cursor.execute(query, (identifier,))
            row = cursor.fetchone()
            if row:
                if row[1] == cls.FOREIGN_TICKER:
                    return ForeignCompany(company_id=row[0], ticker=row[1], name=row[2])
                return DomesticCompany(company_id=row[0], ticker=row[1], name=row[2])

        return None


# =====================================================================
# 5. Execution Block
# =====================================================================
if __name__ == "__main__":
    # Test 1: Fetch domestic company by ticker string
    company_by_ticker = CompanyFactory.get_company("GOOGL")
    if company_by_ticker:
        company_by_ticker.load_time_series()
        company_by_ticker.calculate_bollinger_bands()
        company_by_ticker.assign_grade()
        company_by_ticker.display()

    # Test 2: Fetch foreign company by 4-digit ID
    foreign_company = CompanyFactory.get_company(1001)
    if foreign_company:
        foreign_company.load_time_series()
        foreign_company.calculate_bollinger_bands()
        foreign_company.assign_grade()
        foreign_company.display()

    # Test 3: Fetch domestic company by integer ID (correctly resolves to DomesticCompany)
    domestic_by_id = CompanyFactory.get_company(1)
    if domestic_by_id:
        print(f"Verified ID 1 is resolved as: {type(domestic_by_id).__name__} ({domestic_by_id.name})")

    # Safely close connection on exit
    DatabaseConnection.close_connection()