import tkinter as tk
from tkinter import messagebox
import sqlite3

# Database connection
def get_db():
    return sqlite3.connect("atm.db")

# Login function
def login():
    acc = entry_acc.get()
    pin = entry_pin.get()

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE acc_no=? AND pin=?", (acc, pin))
    result = cur.fetchone()
    conn.close()

    if result:
        global current_acc
        current_acc = acc
        messagebox.showinfo("Success", "Login Successful")
        main_menu()
    else:
        messagebox.showerror("Error", "Invalid Account or PIN")

# Main menu window
def main_menu():
    login_frame.pack_forget()
    menu_frame.pack()

# Balance enquiry
def check_balance():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE acc_no=?", (current_acc,))
    bal = cur.fetchone()[0]
    conn.close()
    messagebox.showinfo("Balance", f"Your Balance: ₹{bal}")

# Deposit
def deposit():
    amt = int(entry_amount.get())
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET balance = balance + ? WHERE acc_no=?", (amt, current_acc))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Amount Deposited")

# Withdraw
def withdraw():
    amt = int(entry_amount.get())
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE acc_no=?", (current_acc,))
    bal = cur.fetchone()[0]

    if amt <= bal:
        cur.execute("UPDATE users SET balance = balance - ? WHERE acc_no=?", (amt, current_acc))
        conn.commit()
        messagebox.showinfo("Success", "Please collect your cash")
    else:
        messagebox.showerror("Error", "Insufficient Balance")

    conn.close()

# GUI setup
root = tk.Tk()
root.title("ATM Simulation")
root.geometry("300x350")

# Login Frame
login_frame = tk.Frame(root)
login_frame.pack()

tk.Label(login_frame, text="ATM Login", font=("Arial", 16)).pack(pady=10)
tk.Label(login_frame, text="Account Number").pack()
entry_acc = tk.Entry(login_frame)
entry_acc.pack()

tk.Label(login_frame, text="PIN").pack()
entry_pin = tk.Entry(login_frame, show="*")
entry_pin.pack()

tk.Button(login_frame, text="Login", command=login).pack(pady=10)

# Menu Frame
menu_frame = tk.Frame(root)

tk.Button(menu_frame, text="Check Balance", width=20, command=check_balance).pack(pady=5)

entry_amount = tk.Entry(menu_frame)
entry_amount.pack(pady=5)
entry_amount.insert(0, "Enter Amount")

tk.Button(menu_frame, text="Deposit", width=20, command=deposit).pack(pady=5)
tk.Button(menu_frame, text="Withdraw", width=20, command=withdraw).pack(pady=5)

root.mainloop()
