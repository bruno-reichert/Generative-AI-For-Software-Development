import random
import sqlite3
import threading
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# =====================================================================
# 1. Singleton Database Connection Class
# =====================================================================
import sqlite3
import threading

class DatabaseConnection:
    """
    An optimized, thread-safe, and configurable Singleton class 
    to manage a single database connection.
    """
    _instance = None
    _lock = threading.Lock()
    
    # Explicitly declare the connection attribute for Pylance
    connection: sqlite3.Connection

    def __new__(cls, db_path: str):
        """Initializes the Singleton with a specific database path."""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance.connection = sqlite3.connect(db_path)
        return cls._instance

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        """Global access point. Raises an error if called before initialization."""
        if cls._instance is None:
            raise RuntimeError(
                "DatabaseConnection has not been initialized. "
                "Call DatabaseConnection('path_to_db.db') first."
            )
        return cls._instance.connection

    @classmethod
    def close_connection(cls):
        """Safely closes the connection and resets the instance."""
        if cls._instance:
            with cls._lock:
                if cls._instance:
                    cls._instance.connection.close()
                    cls._instance = None


# =====================================================================
# 2. Database Schema Creation and Seeding
# =====================================================================
# Initialize the database connection singleton first
DatabaseConnection('company_database.db')

# Retrieve the single connection instance
conn = DatabaseConnection.get_connection()
cursor = conn.cursor()

# Create the companies table
cursor.execute('''
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    name TEXT NOT NULL
)
''')

# Synthesize data for 10 companies
companies = [
    (1, 'AAPL', 'Apple Inc.'),
    (2, 'GOOGL', 'Alphabet Inc.'),
    (3, 'MSFT', 'Microsoft Corporation'),
    (4, 'AMZN', 'Amazon.com Inc.'),
    (5, 'TSLA', 'Tesla Inc.'),
    (6, 'FB', 'Meta Platforms Inc.'),
    (7, 'NVDA', 'NVIDIA Corporation'),
    (8, 'NFLX', 'Netflix Inc.'),
    (9, 'ADBE', 'Adobe Inc.'),
    (10, 'ORCL', 'Oracle Corporation')
]

# Insert data into the companies table
cursor.executemany('''
INSERT OR IGNORE INTO companies (id, ticker, name)
VALUES (?, ?, ?)
''', companies)

# Create the TimeSeries table
cursor.execute('''
CREATE TABLE IF NOT EXISTS TimeSeries (
    id INTEGER PRIMARY KEY,
    company_id INTEGER,
    value REAL,
    date TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id)
)
''')

# Generate synthetic data for TimeSeries table
start_date = datetime(2023, 1, 1)
num_entries = 100

time_series_data = []

for company in companies:
    company_id = company[0]
    for i in range(num_entries):
        date = start_date + timedelta(days=i)
        value = round(random.uniform(100, 500), 2)
        time_series_data.append((company_id, value, date.strftime('%Y-%m-%d')))

# Insert data into the TimeSeries table
cursor.executemany('''
INSERT OR IGNORE INTO TimeSeries (company_id, value, date)
VALUES (?, ?, ?)
''', time_series_data)

# Commit the transaction (we do not close yet, the Singleton holds the connection)
conn.commit()


# =====================================================================
# 3. Domain Model and Calculations
# =====================================================================
# Global parameters
bollinger_width = 2
window_size = 20

class Company:
    def __init__(self, company_id: int, ticker: str, name: str):
        self.company_id = company_id
        self.ticker = ticker
        self.name = name
        
        # Explicitly declare types so Pylance knows they aren't permanently None
        self.time_series: pd.DataFrame | None = None
        self.high_bollinger: pd.Series | None = None
        self.low_bollinger: pd.Series | None = None
        self.moving_average: pd.Series | None = None
        self.grade: str | None = None

    def load_time_series(self):
        conn = DatabaseConnection.get_connection()
        query = '''
        SELECT date, value
        FROM TimeSeries
        WHERE company_id = ?
        ORDER BY date
        '''
        self.time_series = pd.read_sql_query(query, conn, params=(self.company_id,))
        # Convert date column to datetime objects
        self.time_series['date'] = pd.to_datetime(self.time_series['date'])

    def calculate_bollinger_bands(self):
        # Type Guard: Assure Pylance self.time_series is loaded and not None
        if self.time_series is None:
            raise ValueError("Time series must be loaded before calculating bands.")
            
        rolling_mean = self.time_series['value'].rolling(window_size).mean()
        rolling_std = self.time_series['value'].rolling(window_size).std()
        
        self.moving_average = rolling_mean
        self.high_bollinger = rolling_mean + (rolling_std * bollinger_width)
        self.low_bollinger = rolling_mean - (rolling_std * bollinger_width)

    def assign_grade(self):
        # Type Guard: Assure Pylance all calculations exist before checking latest value
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
        # Type Guard
        if (self.time_series is None or 
            self.moving_average is None or 
            self.high_bollinger is None or 
            self.low_bollinger is None):
            raise ValueError("Calculations are incomplete.")
            
        print(f'Company: {self.name} ({self.ticker})')
        print(f'Grade: {self.grade}')
        print('Time Series Data:')
        print(self.time_series.tail())
        print('Moving Average:')
        print(self.moving_average.tail())
        print('High Bollinger Band:')
        print(self.high_bollinger.tail())
        print('Low Bollinger Band:')
        print(self.low_bollinger.tail())


# =====================================================================
# 4. Global Query Helper Functions (Refactored)
# =====================================================================
def get_company_by_ticker(ticker):
    """Fetches a company from the database using the Singleton connection."""
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()
    query = 'SELECT id, ticker, name FROM companies WHERE ticker = ?'
    cursor.execute(query, (ticker,))
    row = cursor.fetchone()
    if row:
        return Company(row[0], row[1], row[2])
    return None

def get_company_by_ticker_or_id(identifier):
    """Fetches a company using the Singleton connection."""
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()
    if isinstance(identifier, int):
        query = 'SELECT id, ticker, name FROM companies WHERE id = ?'
        cursor.execute(query, (identifier,))
    else:
        query = 'SELECT id, ticker, name FROM companies WHERE ticker = ?'
        cursor.execute(query, (identifier,))
    row = cursor.fetchone()
    if row:
        return Company(row[0], row[1], row[2])
    return None


# =====================================================================
# 5. Execution Block
# =====================================================================
if __name__ == "__main__":
    # Get company by ticker - Notice we do not pass the connection here anymore!
    company = get_company_by_ticker('GOOGL')
    if company:
        company.load_time_series()
        company.calculate_bollinger_bands()
        company.assign_grade()
        company.display()

    # Safely close the database connection upon application shutdown
    DatabaseConnection.close_connection()