# Advanced ATM Simulation

A powerful ATM simulation application built with Python using the `Tkinter` library for the Graphical User Interface (GUI) and `SQLite3` for database management.

## Features

- **User Authentication**: Secure login system using Account Number and PIN.
- **Account Registration**: Create new user accounts dynamically from the login screen!
- **Check Balance**: View real-time current balance.
- **Deposit & Withdraw Funds**: Modify your balance securely with input validation.
- **Transfer Funds**: Send money instantly to any other existing account in the database.
- **Change PIN**: Update your security PIN securely.
- **Mini Statement**: View your transaction history (last 15 deposits, withdrawals, transfers).
- **Logout Functionality**: Safely logout and clear user session.
- **Error Handling**: Full input validation for all inputs.

## Project Structure

- `atm.py`: The main OOP script that handles multiple frames and runs the Tkinter ATM GUI.
- `create_db.py`: A setup script to initialize the SQLite database, transactions table, and create a sample user.
- `atm.db`: SQLite database file (generated after running `create_db.py`).

## Prerequisites

- Python 3.x installed on your system.

## Setup Instructions

1. **Initialize Database**:
   Run the `create_db.py` script to generate the database with the required tables and a sample user.
   ```bash
   python create_db.py
   ```

2. **Run the Application**:
   Run the main application script `atm.py`.
   ```bash
   python atm.py
   ```

## Default Sample Credentials

After running `create_db.py`, a default user is created to test the application:

- **Account Number**: `123456`
- **PIN**: `1234`
- **Initial Balance**: `₹10,000`

## How to Use

1. Launch the app.
2. Either use the sample credentials to **Login**, or click **Create New Account** to register your own custom account (like `12107721`)!
3. On the Main Menu, you can check your balance, view your mini statement, transfer funds, or change your PIN.
4. You can also use the **Quick Transactions** section to deposit or withdraw money.
5. Click **Logout** to end the session safely.

## Technologies Used

- **Python**: Core programming language.
- **Tkinter**: Python's standard GUI library with OOP integration.
- **SQLite3**: Relational database for persistent storage.
