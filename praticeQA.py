import unittest
import time
from datetime import datetime, timedelta
from pratice import DigitalWalletSystem

class WalletSecurityQA(unittest.TestCase):
    def setUp(self):
        self.sys = DigitalWalletSystem()
        self.sys.create_account("ACC001", "1234", "Alice")
        self.sys.create_account("ACC002", "5678", "Bob")
        self.sys.deposit("ACC001", 10000.0)  # Seed fund for operations

    def test_normal_transaction(self):
        """Test a clean money transfer under normal operational limits."""
        status, msg = self.sys.execute_transaction("ACC001", "ACC002", 100.0, "1234", "TRANSFER")
        self.assertEqual(status, "SUCCESS")
        self.assertEqual(self.sys.verify_balance("ACC001")[0], 9900.0)
        self.assertEqual(self.sys.verify_balance("ACC002")[0], 100.0)

    def test_insufficient_balance(self):
        """Test that a transaction fails when balance is too low."""
        status, msg = self.sys.execute_transaction("ACC002", "ACC001", 50.0, "5678", "TRANSFER")
        self.assertEqual(status, "FAILED")
        self.assertIn("Insufficient balance", msg)

    def test_daily_limit(self):
        """Test that transactions exceeding the custom daily cap are rejected."""
        status, msg = self.sys.execute_transaction("ACC001", "ACC002", 5001.0, "1234", "TRANSFER")
        self.assertEqual(status, "FAILED")
        self.assertIn("Daily transaction limit exceeded", msg)

    def test_multiple_failed_pins(self):
        """Test security lockout triggered after 3 consecutive wrong PIN evaluations."""
        # Attempt 1
        status, msg = self.sys.execute_transaction("ACC001", "ACC002", 10.0, "9999", "TRANSFER")
        self.assertEqual(status, "FAILED")
        # Attempt 2
        status, msg = self.sys.execute_transaction("ACC001", "ACC002", 10.0, "8888", "TRANSFER")
        self.assertEqual(status, "FAILED")
        # Attempt 3 - Lockout triggers
        status, msg = self.sys.execute_transaction("ACC001", "ACC002", 10.0, "7777", "TRANSFER")
        self.assertEqual(status, "FAILED")
        self.assertIn("Account has been locked", msg)
        
        # Check subsequent attempt on locked profile
        status, msg = self.sys.execute_transaction("ACC001", "ACC002", 10.0, "1234", "TRANSFER")
        self.assertIn("Account locked", msg)

    def test_suspicious_transaction_large_amount(self):
        """Test fraud flag when amount meets or exceeds the large transaction metric."""
        status, msg = self.sys.execute_transaction("ACC001", "ACC002", 2500.0, "1234", "TRANSFER")
        self.assertEqual(status, "SUSPICIOUS")
        self.assertIn("Large transaction flagged", msg)

    def test_suspicious_transaction_velocity(self):
        """Test fraud engine flags velocity of over 5 transactions in a tight timeline."""
        # Generate 5 rapid normal transactions
        for _ in range(5):
            self.sys.execute_transaction("ACC001", "ACC002", 5.0, "1234", "TRANSFER")
            
        # The 6th rapid transaction should trip the fraud warning engine
        status, msg = self.sys.execute_transaction("ACC001", "ACC002", 5.0, "1234", "TRANSFER")
        self.assertEqual(status, "SUSPICIOUS")
        self.assertIn("High transaction velocity", msg)

    def test_duplicate_transaction(self):
        """Test system tags rapid matching sequential allocations as duplicate fraud patterns."""
        status1, _ = self.sys.execute_transaction("ACC001", "ACC002", 45.0, "1234", "TRANSFER")
        status2, msg2 = self.sys.execute_transaction("ACC001", "ACC002", 45.0, "1234", "TRANSFER")
        
        self.assertEqual(status1, "SUCCESS")
        self.assertEqual(status2, "SUSPICIOUS")
        self.assertIn("Potential duplicate transaction detected", msg2)

    def test_negative_amount(self):
        """Test payload parameter guards against logic exploitation via negative integers."""
        status, msg = self.sys.execute_transaction("ACC001", "ACC002", -50.0, "1234", "TRANSFER")
        self.assertEqual(status, "FAILED")
        self.assertIn("Negative or zero amount not allowed", msg)

    def test_concurrent_transactions_simulation(self):
        """Simulates parallel execution logic safety by verifying state mutations hold up securely."""
        import threading
        
        errors = []
        def worker():
            status, msg = self.sys.execute_transaction("ACC001", "ACC002", 10.0, "1234", "TRANSFER")
            if status == "FAILED":
                errors.append(msg)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads: t.start()
        for t in threads: t.join()

        # Check total remaining balance balances accurately out to 10 * 10 = 100 deducted
        bal, _ = self.sys.verify_balance("ACC001")
        self.assertEqual(bal, 9900.0)

if __name__ == "__main__":
    unittest.main()
