import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3

class ATMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced ATM Simulation")
        self.root.geometry("450x600")
        self.root.resizable(False, False)
        
        self.current_acc = None
        
        # Fonts
        self.app_font = ("Helvetica", 12)
        self.title_font = ("Helvetica", 18, "bold")
        self.small_font = ("Helvetica", 10)
        
        # Container for all frames
        self.container = tk.Frame(root)
        self.container.pack(fill="both", expand=True)
        
        self.frames = {}
        
        self.create_frames()
        self.show_frame("LoginFrame")

    def get_db(self):
        return sqlite3.connect("atm.db")

    def create_frames(self):
        # Initialize all frames
        for F in (LoginFrame, RegisterFrame, MainMenuFrame, TransferFrame, PinChangeFrame, HistoryFrame):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if page_name == "HistoryFrame" and self.current_acc:
            frame.load_history()
        elif page_name == "MainMenuFrame":
            frame.reset_amount_entry()
        frame.tkraise()
        
    def log_transaction(self, acc_no, t_type, amount):
        try:
            conn = self.get_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO transactions (acc_no, type, amount) VALUES (?, ?, ?)", 
                       (acc_no, t_type, amount))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print("Transaction log error:", e)

class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        tk.Label(self, text="Welcome to ATM", font=controller.title_font).pack(pady=40)
        
        tk.Label(self, text="Account Number:", font=controller.app_font).pack(pady=5)
        self.entry_acc = tk.Entry(self, font=controller.app_font, width=25)
        self.entry_acc.pack()
        
        tk.Label(self, text="PIN:", font=controller.app_font).pack(pady=5)
        self.entry_pin = tk.Entry(self, font=controller.app_font, width=25, show="*")
        self.entry_pin.pack()
        
        tk.Button(self, text="Login", font=controller.app_font, bg="#4CAF50", fg="white", 
                  width=20, command=self.login).pack(pady=20)
                  
        tk.Label(self, text="Don't have an account?", font=controller.small_font).pack(pady=(20,5))
        tk.Button(self, text="Create New Account", font=controller.small_font, bg="#2196F3", fg="white",
                  width=20, command=lambda: controller.show_frame("RegisterFrame")).pack(pady=5)

    def login(self):
        acc = self.entry_acc.get()
        pin = self.entry_pin.get()

        if not acc or not pin:
            messagebox.showwarning("Warning", "Please enter both Account Number and PIN")
            return

        try:
            conn = self.controller.get_db()
            cur = conn.cursor()
            cur.execute("SELECT balance FROM users WHERE acc_no=? AND pin=?", (acc, pin))
            result = cur.fetchone()
            conn.close()

            if result:
                self.controller.current_acc = acc
                messagebox.showinfo("Success", "Login Successful")
                self.entry_acc.delete(0, tk.END)
                self.entry_pin.delete(0, tk.END)
                self.controller.show_frame("MainMenuFrame")
            else:
                messagebox.showerror("Error", "Invalid Account Number or PIN")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

class RegisterFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        tk.Label(self, text="Create New Account", font=controller.title_font).pack(pady=30)
        
        tk.Label(self, text="Choose Account Number:", font=controller.app_font).pack(pady=5)
        self.entry_acc = tk.Entry(self, font=controller.app_font, width=25)
        self.entry_acc.pack()
        
        tk.Label(self, text="Choose a PIN:", font=controller.app_font).pack(pady=5)
        self.entry_pin = tk.Entry(self, font=controller.app_font, width=25, show="*")
        self.entry_pin.pack()
        
        tk.Label(self, text="Initial Deposit (₹):", font=controller.app_font).pack(pady=5)
        self.entry_dep = tk.Entry(self, font=controller.app_font, width=25)
        self.entry_dep.pack()
        
        tk.Button(self, text="Register", font=controller.app_font, bg="#4CAF50", fg="white", 
                  width=20, command=self.register).pack(pady=20)
        
        tk.Button(self, text="Back to Login", font=controller.app_font, bg="#9e9e9e", fg="black", 
                  width=20, command=lambda: controller.show_frame("LoginFrame")).pack(pady=5)

    def register(self):
        acc = self.entry_acc.get()
        pin = self.entry_pin.get()
        dep_str = self.entry_dep.get()
        
        if not acc or not pin or not dep_str:
            messagebox.showwarning("Warning", "All fields are required")
            return
            
        try:
            dep = float(dep_str)
            if dep < 0:
                messagebox.showwarning("Warning", "Initial deposit cannot be negative")
                return
                
            conn = self.controller.get_db()
            cur = conn.cursor()
            
            cur.execute("SELECT * FROM users WHERE acc_no=?", (acc,))
            if cur.fetchone():
                messagebox.showerror("Error", "Account Number already exists! Please choose another.")
                conn.close()
                return
                
            cur.execute("INSERT INTO users (acc_no, pin, balance) VALUES (?, ?, ?)", (acc, pin, dep))
            conn.commit()
            conn.close()
            
            if dep > 0:
                self.controller.log_transaction(acc, "Initial Deposit", dep)
                
            messagebox.showinfo("Success", "Account created successfully! You can now login.")
            self.entry_acc.delete(0, tk.END)
            self.entry_pin.delete(0, tk.END)
            self.entry_dep.delete(0, tk.END)
            self.controller.show_frame("LoginFrame")
            
        except ValueError:
            messagebox.showerror("Error", "Deposit must be a valid number")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

class MainMenuFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        tk.Label(self, text="ATM Main Menu", font=controller.title_font).pack(pady=20)
        
        # Action Buttons Container
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Check Balance", font=controller.app_font, width=15, bg="#2196F3", fg="white", 
                  command=self.check_balance).grid(row=0, column=0, padx=10, pady=10)
        
        tk.Button(btn_frame, text="Mini Statement", font=controller.app_font, width=15, bg="#00BCD4", fg="white", 
                  command=lambda: controller.show_frame("HistoryFrame")).grid(row=0, column=1, padx=10, pady=10)
        
        tk.Button(btn_frame, text="Transfer Funds", font=controller.app_font, width=15, bg="#FF9800", fg="white", 
                  command=lambda: controller.show_frame("TransferFrame")).grid(row=1, column=0, padx=10, pady=10)
                  
        tk.Button(btn_frame, text="Change PIN", font=controller.app_font, width=15, bg="#673AB7", fg="white", 
                  command=lambda: controller.show_frame("PinChangeFrame")).grid(row=1, column=1, padx=10, pady=10)
        
        # Divider
        tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=20, pady=15)
        
        # Fast Actions
        tk.Label(self, text="Quick Transactions", font=("Helvetica", 14, "bold")).pack()
        
        op_frame = tk.Frame(self)
        op_frame.pack(pady=10)
        
        self.entry_amount = tk.Entry(op_frame, font=controller.app_font, width=20, justify='center')
        self.entry_amount.pack(pady=10)
        self.entry_amount.bind("<FocusIn>", self.clear_placeholder)
        self.entry_amount.bind("<FocusOut>", self.restore_placeholder)
        
        tk.Button(op_frame, text="Deposit", font=controller.app_font, width=15, bg="#4CAF50", fg="white", 
                  command=self.deposit).pack(side=tk.LEFT, padx=10)
        tk.Button(op_frame, text="Withdraw", font=controller.app_font, width=15, bg="#f44336", fg="white", 
                  command=self.withdraw).pack(side=tk.LEFT, padx=10)
        
        tk.Button(self, text="Logout", font=controller.app_font, width=20, bg="#9e9e9e", fg="black", 
                  command=self.logout).pack(pady=30)

    def clear_placeholder(self, event):
        if self.entry_amount.get() == "Enter Amount":
            self.entry_amount.delete(0, tk.END)
            self.entry_amount.config(fg='black')

    def restore_placeholder(self, event):
        if not self.entry_amount.get():
            self.reset_amount_entry()

    def reset_amount_entry(self):
        self.entry_amount.delete(0, tk.END)
        self.entry_amount.insert(0, "Enter Amount")
        self.entry_amount.config(fg='gray')

    def check_balance(self):
        try:
            conn = self.controller.get_db()
            cur = conn.cursor()
            cur.execute("SELECT balance FROM users WHERE acc_no=?", (self.controller.current_acc,))
            bal = cur.fetchone()[0]
            conn.close()
            messagebox.showinfo("Balance", f"Your Current Balance is: ₹{bal:.2f}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def deposit(self):
        amount_str = self.entry_amount.get()
        try:
            amt = float(amount_str)
            if amt <= 0:
                messagebox.showwarning("Warning", "Amount must be greater than zero")
                return
                
            conn = self.controller.get_db()
            cur = conn.cursor()
            cur.execute("UPDATE users SET balance = balance + ? WHERE acc_no=?", (amt, self.controller.current_acc))
            conn.commit()
            conn.close()
            
            self.controller.log_transaction(self.controller.current_acc, "Deposit", amt)
            messagebox.showinfo("Success", f"₹{amt:.2f} Deposited Successfully")
            self.reset_amount_entry()
            self.controller.root.focus()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric amount")
            
    def withdraw(self):
        amount_str = self.entry_amount.get()
        try:
            amt = float(amount_str)
            if amt <= 0:
                messagebox.showwarning("Warning", "Amount must be greater than zero")
                return

            conn = self.controller.get_db()
            cur = conn.cursor()
            cur.execute("SELECT balance FROM users WHERE acc_no=?", (self.controller.current_acc,))
            bal = cur.fetchone()[0]

            if amt <= bal:
                cur.execute("UPDATE users SET balance = balance - ? WHERE acc_no=?", (amt, self.controller.current_acc))
                conn.commit()
                self.controller.log_transaction(self.controller.current_acc, "Withdrawal", amt)
                messagebox.showinfo("Success", f"Please collect your cash: ₹{amt:.2f}")
                self.reset_amount_entry()
                self.controller.root.focus()
            else:
                messagebox.showerror("Error", "Insufficient Balance")
            conn.close()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric amount")

    def logout(self):
        self.controller.current_acc = None
        messagebox.showinfo("Logged Out", "You have been successfully logged out.")
        self.controller.show_frame("LoginFrame")

class TransferFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        tk.Label(self, text="Transfer Funds", font=controller.title_font).pack(pady=40)
        
        tk.Label(self, text="Recipient Account Number:", font=controller.app_font).pack(pady=5)
        self.entry_acc = tk.Entry(self, font=controller.app_font, width=25)
        self.entry_acc.pack()
        
        tk.Label(self, text="Amount to Transfer (₹):", font=controller.app_font).pack(pady=5)
        self.entry_amt = tk.Entry(self, font=controller.app_font, width=25)
        self.entry_amt.pack()
        
        tk.Button(self, text="Send Money", font=controller.app_font, bg="#FF9800", fg="white", 
                  width=20, command=self.transfer).pack(pady=30)
        
        tk.Button(self, text="Back to Menu", font=controller.app_font, bg="#9e9e9e", fg="black", width=20, 
                  command=lambda: controller.show_frame("MainMenuFrame")).pack(pady=5)

    def transfer(self):
        target_acc = self.entry_acc.get()
        amt_str = self.entry_amt.get()
        
        if not target_acc or not amt_str:
            messagebox.showwarning("Warning", "All fields are required")
            return
            
        if target_acc == self.controller.current_acc:
            messagebox.showerror("Error", "You cannot transfer to your own account!")
            return
            
        try:
            amt = float(amt_str)
            if amt <= 0:
                messagebox.showwarning("Warning", "Amount must be greater than zero")
                return
                
            conn = self.controller.get_db()
            cur = conn.cursor()
            
            # Check target exists
            cur.execute("SELECT * FROM users WHERE acc_no=?", (target_acc,))
            if not cur.fetchone():
                messagebox.showerror("Error", "Recipient Account not found in our system")
                conn.close()
                return
                
            # Check balance
            cur.execute("SELECT balance FROM users WHERE acc_no=?", (self.controller.current_acc,))
            bal = cur.fetchone()[0]
            
            if amt <= bal:
                cur.execute("UPDATE users SET balance = balance - ? WHERE acc_no=?", (amt, self.controller.current_acc))
                cur.execute("UPDATE users SET balance = balance + ? WHERE acc_no=?", (amt, target_acc))
                conn.commit()
                
                self.controller.log_transaction(self.controller.current_acc, f"Transfer To {target_acc}", amt)
                self.controller.log_transaction(target_acc, f"Transfer From {self.controller.current_acc}", amt)
                
                messagebox.showinfo("Success", f"₹{amt:.2f} sent successfully to Account {target_acc}")
                self.entry_acc.delete(0, tk.END)
                self.entry_amt.delete(0, tk.END)
                self.controller.show_frame("MainMenuFrame")
            else:
                messagebox.showerror("Error", "Insufficient Balance to complete transfer")
                
            conn.close()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric amount")

class PinChangeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        tk.Label(self, text="Change Security PIN", font=controller.title_font).pack(pady=40)
        
        tk.Label(self, text="Current PIN:", font=controller.app_font).pack(pady=5)
        self.entry_old = tk.Entry(self, font=controller.app_font, width=25, show="*")
        self.entry_old.pack()
        
        tk.Label(self, text="New PIN:", font=controller.app_font).pack(pady=5)
        self.entry_new = tk.Entry(self, font=controller.app_font, width=25, show="*")
        self.entry_new.pack()
        
        tk.Button(self, text="Update PIN", font=controller.app_font, bg="#673AB7", fg="white", 
                  width=20, command=self.change_pin).pack(pady=30)
        
        tk.Button(self, text="Back to Menu", font=controller.app_font, bg="#9e9e9e", fg="black", width=20, 
                  command=lambda: controller.show_frame("MainMenuFrame")).pack(pady=5)

    def change_pin(self):
        old_pin = self.entry_old.get()
        new_pin = self.entry_new.get()
        
        if not old_pin or not new_pin:
            messagebox.showwarning("Warning", "All fields are required")
            return
            
        conn = self.controller.get_db()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM users WHERE acc_no=? AND pin=?", (self.controller.current_acc, old_pin))
        if cur.fetchone():
            cur.execute("UPDATE users SET pin=? WHERE acc_no=?", (new_pin, self.controller.current_acc))
            conn.commit()
            messagebox.showinfo("Success", "Your PIN has been updated successfully!")
            self.entry_old.delete(0, tk.END)
            self.entry_new.delete(0, tk.END)
            self.controller.show_frame("MainMenuFrame")
        else:
            messagebox.showerror("Error", "Incorrect Current PIN")
            
        conn.close()

class HistoryFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        tk.Label(self, text="Transaction History", font=controller.title_font).pack(pady=20)
        
        # Treeview for history
        columns = ("Date", "Type", "Amount")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        self.tree.heading("Date", text="Date")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Amount", text="Amount (₹)")
        
        self.tree.column("Date", width=140, anchor="center")
        self.tree.column("Type", width=140, anchor="center")
        self.tree.column("Amount", width=120, anchor="e")
        
        self.tree.pack(pady=10, padx=20, fill="both", expand=True)
        
        tk.Button(self, text="Back to Menu", font=controller.app_font, bg="#9e9e9e", fg="black", width=20, 
                  command=lambda: controller.show_frame("MainMenuFrame")).pack(pady=20)

    def load_history(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        conn = self.controller.get_db()
        cur = conn.cursor()
        cur.execute("SELECT date, type, amount FROM transactions WHERE acc_no=? ORDER BY date DESC LIMIT 15", 
                   (self.controller.current_acc,))
        records = cur.fetchall()
        conn.close()
        
        for rec in records:
            dt = rec[0].split('.')[0] if '.' in rec[0] else rec[0]
            amt = f"₹{rec[2]:.2f}"
            self.tree.insert("", "end", values=(dt, rec[1], amt))

if __name__ == "__main__":
    root = tk.Tk()
    app = ATMApp(root)
    root.mainloop()
