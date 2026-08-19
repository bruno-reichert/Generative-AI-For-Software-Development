import unittest
import pandas as pd
from after import (
    DatabaseConnection,
    CompanyFactory,
    DomesticCompany,
    ForeignCompany,
    CryptoCompany,
)


class TestCompanySystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Ensure the Singleton connection is active before running tests."""
        DatabaseConnection('company_database.db')

    @classmethod
    def tearDownClass(cls):
        """Clean up singleton connection after all tests finish."""
        DatabaseConnection.close_connection()

    # -----------------------------------------------------------------
    # 1. Singleton Tests
    # -----------------------------------------------------------------
    def test_database_connection_singleton(self):
        """Verify that get_connection() returns the exact same object reference."""
        conn1 = DatabaseConnection.get_connection()
        conn2 = DatabaseConnection.get_connection()
        self.assertIs(conn1, conn2, "DatabaseConnection must return the same instance.")

    # -----------------------------------------------------------------
    # 2. Factory Pattern & Subclass Routing Tests
    # -----------------------------------------------------------------
    def test_factory_domestic_lookup(self):
        """Verify domestic company resolution by both ticker and ID."""
        by_ticker = CompanyFactory.get_company("AAPL")
        self.assertIsInstance(by_ticker, DomesticCompany)
        self.assertEqual(by_ticker.company_type, "Domestic")
        self.assertIn("AAPL", by_ticker.get_identifier())

        by_id = CompanyFactory.get_company(1)
        self.assertIsInstance(by_id, DomesticCompany)
        self.assertEqual(by_id.name, "Apple Inc.")

    def test_factory_foreign_lookup(self):
        """Verify foreign company resolution by 4-digit ID."""
        foreign = CompanyFactory.get_company(1001)
        self.assertIsInstance(foreign, ForeignCompany)
        self.assertEqual(foreign.company_type, "Foreign")
        self.assertIn("1001", foreign.get_identifier())
        self.assertEqual(foreign.ticker, "ZZZZ")

    def test_factory_crypto_lookup(self):
        """Verify crypto resolution by '-USD' ticker pair and 5000+ ID."""
        by_ticker = CompanyFactory.get_company("BTC-USD")
        self.assertIsInstance(by_ticker, CryptoCompany)
        self.assertEqual(by_ticker.company_type, "Crypto")
        self.assertIn("24/7 Market", by_ticker.get_identifier())

        by_id = CompanyFactory.get_company(5002)
        self.assertIsInstance(by_id, CryptoCompany)
        self.assertEqual(by_id.name, "Ethereum")

    def test_factory_non_existent_entity(self):
        """Verify that non-existent identifiers return None."""
        self.assertIsNone(CompanyFactory.get_company("INVALID_TICKER"))
        self.assertIsNone(CompanyFactory.get_company(99999))

    # -----------------------------------------------------------------
    # 3. Calculation & Pipeline Tests
    # -----------------------------------------------------------------
    def test_time_series_and_bollinger_calculation(self):
        """Verify end-to-end execution of load -> calculate -> grade."""
        entity = CompanyFactory.get_company("BTC-USD")
        self.assertIsNotNone(entity)
        assert entity is not None  # Type narrowing for Pylance

        # Load time series
        entity.load_time_series()
        self.assertIsInstance(entity.time_series, pd.DataFrame)
        self.assertEqual(len(entity.time_series), 100)

        # Calculate indicators
        entity.calculate_bollinger_bands()
        self.assertIsNotNone(entity.moving_average)
        self.assertIsNotNone(entity.high_bollinger)
        self.assertIsNotNone(entity.low_bollinger)

        # Assign grade
        entity.assign_grade()
        self.assertIn(entity.grade, ["A", "B", "C"])

    # -----------------------------------------------------------------
    # 4. Domain Constraint Guards
    # -----------------------------------------------------------------
    def test_id_range_validation_guards(self):
        """Verify that invalid ID ranges raise ValueError at construction."""
        # Foreign company must be 1000 - 4999
        with self.assertRaises(ValueError):
            ForeignCompany(company_id=50, ticker="ZZZZ", name="Invalid Foreign")

        # Crypto company must be >= 5000
        with self.assertRaises(ValueError):
            CryptoCompany(company_id=4999, ticker="DOGE-USD", name="Invalid Crypto")


if __name__ == "__main__":
    unittest.main(verbosity=2)