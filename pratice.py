# 1. Dictionary storing student details (ID as key, details as nested dictionary)
import time
from datetime import datetime, timedelta

class Transaction:
    def __init__(self, sender_id, recipient_id, amount, t_type, status="SUCCESS"):
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.amount = amount
        self.type = t_type  # "DEPOSIT", "WITHDRAWAL", "TRANSFER"
        self.timestamp = datetime.now()
        self.status = status  # "SUCCESS", "FAILED", "SUSPICIOUS"

class Account:
    def __init__(self, account_id, pin, name, daily_limit=5000.0, large_tx_threshold=2000.0):
        self.account_id = account_id
        self.pin = pin
        self.name = name
        self.balance = 0.0
        self.daily_limit = daily_limit
        self.large_tx_threshold = large_tx_threshold
        self.failed_pin_attempts = 0
        self.is_locked = False
        self.history = []
        self.daily_spent = 0.0
        self.last_reset_date = datetime.now().date()

    def reset_daily_limit_if_new_day(self):
        current_date = datetime.now().date()
        if current_date > self.last_reset_date:
            self.daily_spent = 0.0
            self.last_reset_date = current_date

    def get_average_transaction_amount(self):
        successful_txs = [tx.amount for tx in self.history if tx.status == "SUCCESS" and tx.type in ["WITHDRAWAL", "TRANSFER"]]
        if not successful_txs:
            return 0.0
        return sum(successful_txs) / len(successful_txs)


class DigitalWalletSystem:
    def __init__(self):
        self.accounts = {}

    def create_account(self, account_id, pin, name, daily_limit=5000.0):
        """Creates a new digital wallet account."""
        if account_id in self.accounts:
            return False, "Account already exists."
        self.accounts[account_id] = Account(account_id, pin, name, daily_limit)
        return True, f"Account {account_id} created successfully."

    def verify_balance(self, account_id):
        """Verifies the balance of an account."""
        if account_id not in self.accounts:
            return None, "Account not found."
        return self.accounts[account_id].balance, "Success"

    def deposit(self, account_id, amount):
        """Deposits a positive amount into an account."""
        if account_id not in self.accounts:
            return False, "Account not found."
        if amount <= 0:
            return False, "Negative or zero amount not allowed."
        
        account = self.accounts[account_id]
        account.balance += amount
        account.history.append(Transaction(account_id, account_id, amount, "DEPOSIT"))
        return True, f"Deposited ${amount:.2f} successfully."

    def execute_transaction(self, sender_id, recipient_id, amount, pin, t_type):
        """Handles Withdrawals and Money Transfers with unified security rules."""
        if sender_id not in self.accounts:
            return "FAILED", "Sender account not found."
        
        sender = self.accounts[sender_id]
        sender.reset_daily_limit_if_new_day()

        # Rule Check: Account Lock Status
        if sender.is_locked:
            return "FAILED", "Account locked due to too many failed PIN attempts."

        # Rule Check: Negative or Zero Amount
        if amount <= 0:
            return "FAILED", "Negative or zero amount not allowed."

        # Rule Check: PIN Verification (Fraud Indicator)
        if sender.pin != pin:
            sender.failed_pin_attempts += 1
            if sender.failed_pin_attempts >= 3:
                sender.is_locked = True
                return "FAILED", "Incorrect PIN. Account has been locked."
            return "FAILED", f"Incorrect PIN. Attempts remaining: {3 - sender.failed_pin_attempts}"
        
        # Reset failed attempts on a successful PIN authentication
        sender.failed_pin_attempts = 0

        # Rule Check: Balance Verification
        if sender.balance < amount:
            sender.history.append(Transaction(sender_id, recipient_id, amount, t_type, "FAILED"))
            return "FAILED", "Insufficient balance."

        # Rule Check: Daily Limit Verification
        if sender.daily_spent + amount > sender.daily_limit:
            sender.history.append(Transaction(sender_id, recipient_id, amount, t_type, "FAILED"))
            return "FAILED", "Daily transaction limit exceeded."

        # --- FRAUD DETECTION ENGINE ---
        is_suspicious = False
        fraud_reasons = []
        now = datetime.now()

        # 1. Frequency Fraud Check: More than 5 transactions within the last 10 minutes
        ten_mins_ago = now - timedelta(minutes=10)
        recent_tx_count = sum(1 for tx in sender.history if tx.timestamp >= ten_mins_ago)
        if recent_tx_count >= 5:
            is_suspicious = True
            fraud_reasons.append("High transaction velocity (>5 tx in 10 mins)")

        # 2. Large Transaction Fraud Check
        if amount >= sender.large_tx_threshold:
            is_suspicious = True
            fraud_reasons.append(f"Large transaction flagged (>= ${sender.large_tx_threshold})")

        # 3. Unusual Transaction Amount Check (More than 4x historical average if history exists)
        avg_amount = sender.get_average_transaction_amount()
        if avg_amount > 0 and amount > (avg_amount * 4):
            is_suspicious = True
            fraud_reasons.append("Unusual transaction volume relative to historical average")

        # 4. Duplicate Transaction Check (Same recipient & amount within past 60 seconds)
        one_min_ago = now - timedelta(seconds=60)
        duplicate_exists = any(
            tx.recipient_id == recipient_id and tx.amount == amount and tx.status == "SUCCESS" and tx.timestamp >= one_min_ago
            for tx in sender.history
        )
        if duplicate_exists:
            is_suspicious = True
            fraud_reasons.append("Potential duplicate transaction detected")

        # Execute Financial Changes
        status = "SUSPICIOUS" if is_suspicious else "SUCCESS"
        sender.balance -= amount
        sender.daily_spent += amount
        
        if t_type == "TRANSFER":
            if recipient_id not in self.accounts:
                return "FAILED", "Recipient account not found."
            recipient = self.accounts[recipient_id]
            recipient.balance += amount
            recipient.history.append(Transaction(sender_id, recipient_id, amount, "RECEIVE", status))

        sender.history.append(Transaction(sender_id, recipient_id, amount, t_type, status))

        if is_suspicious:
            return "SUSPICIOUS", f"Transaction flagged as suspicious. Reasons: {'; '.join(fraud_reasons)}"
        return "SUCCESS", f"Transaction executed successfully via {t_type}."

    def get_transaction_history(self, account_id):
        """Returns the full transaction logs for a profile."""
        if account_id not in self.accounts:
            return None
        return self.accounts[account_id].history
    
    # --- ADD THIS TO THE BOTTOM OF YOUR pratice.py FILE ---
if __name__ == "__main__":
    # 1. Initialize the system
    sys = DigitalWalletSystem()
    print(" Digital Wallet System Initialized.")
    
    # 2. Create accounts
    sys.create_account("ACC001", "1234", "Alice")
    sys.create_account("ACC002", "5678", "Bob")
    
    # 3. Add initial deposit
    success, msg = sys.deposit("ACC001", 5000.0)
    print(f"Deposit Status: {msg} | Balance: ${sys.verify_balance('ACC001')[0]}")
    
    # 4. Perform a normal transaction
    status, msg = sys.execute_transaction("ACC001", "ACC002", 150.0, "1234", "TRANSFER")
    print(f"Transaction Status: {status} | Details: {msg}")
    print(f"Alice Balance: ${sys.verify_balance('ACC001')[0]}")
    print(f"Bob Balance: ${sys.verify_balance('ACC002')[0]}")

    # 5. Trigger a fraud check (Large Transaction Threshold >= 2000)
    status, msg = sys.execute_transaction("ACC001", "ACC002", 2500.0, "1234", "TRANSFER")
    print(f"\nFraud Check Status: {status}")
    print(f"Details: {msg}")

