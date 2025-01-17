import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import re
from datetime import datetime
from typing import List, Tuple

class DatabaseManager:
    DB_NAME = "mentor.db"

    @staticmethod
    def connect():
        return sqlite3.connect(DatabaseManager.DB_NAME)

    @staticmethod
    def fetch_all(query: str, params: tuple = ()) -> List[tuple]:
        with DatabaseManager.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def execute(query: str, params: tuple = ()):
        with DatabaseManager.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

class QATab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(self.frame, text="Question:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_question = ttk.Entry(self.frame, width=40, font=("Helvetica", 9))
        self.entry_question.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self.frame, text="Answer:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_answer = ttk.Entry(self.frame, width=40, font=("Helvetica", 9))
        self.entry_answer.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(self.frame, text="Add/Update Q&A", command=self.add_qa, style="Small.TButton", width=15).grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")

        self.tree = self.create_treeview(self.frame, ["Question", "Answer", "Timestamp"])
        self.tree.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        ttk.Button(self.frame, text="Delete Selected", command=self.delete_qa, style="Small.TButton", width=15).grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")

        # Configure grid weights to make the treeview expand
        self.frame.grid_rowconfigure(3, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

    def create_treeview(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150 if col != "Description" else 300)
        return tree

    def add_qa(self):
        question = self.entry_question.get().strip()
        answer = self.entry_answer.get().strip()
        if question and answer:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            existing = DatabaseManager.fetch_all("SELECT timestamp FROM qa WHERE question = ?", (question,))
            if existing:
                existing_timestamp = existing[0][0]
                if timestamp > existing_timestamp:
                    DatabaseManager.execute("DELETE FROM qa WHERE question = ?", (question,))
            DatabaseManager.execute("INSERT INTO qa (question, answer, timestamp) VALUES (?, ?, ?)", (question, answer, timestamp))
            self.refresh_list()
            self.entry_question.delete(0, tk.END)
            self.entry_answer.delete(0, tk.END)
            messagebox.showinfo("Success", "Question and answer added/updated.")
        else:
            messagebox.showwarning("Warning", "Please fill in both fields.")

    def delete_qa(self):
        selected = self.tree.selection()
        if selected:
            item_value = self.tree.item(selected[0], "values")[0]
            DatabaseManager.execute("DELETE FROM qa WHERE question = ?", (item_value,))
            self.refresh_list()
            messagebox.showinfo("Success", "Item deleted successfully.")
        else:
            messagebox.showwarning("Warning", "Please select an item.")

    def refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        data = DatabaseManager.fetch_all("SELECT question, answer, timestamp FROM qa")
        for record in data:
            self.tree.insert("", tk.END, values=record)

class MenuTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(self.frame, text="Item Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_name = ttk.Entry(self.frame, width=30, font=("Helvetica", 9))
        self.entry_name.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self.frame, text="Price (Toman):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_price = ttk.Entry(self.frame, width=30, font=("Helvetica", 9))
        self.entry_price.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self.frame, text="Description:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_description = ttk.Entry(self.frame, width=30, font=("Helvetica", 9))
        self.entry_description.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(self.frame, text="Add/Update Menu Item", command=self.add_menu_item, style="Small.TButton", width=15).grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")

        self.tree = self.create_treeview(self.frame, ["Name", "Price", "Description", "Timestamp"])
        self.tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        ttk.Button(self.frame, text="Delete Selected", command=self.delete_menu_item, style="Small.TButton", width=15).grid(row=5, column=0, columnspan=2, pady=5, sticky="ew")

        # Configure grid weights to make the treeview expand
        self.frame.grid_rowconfigure(4, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

    def create_treeview(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150 if col != "Description" else 300)
        return tree

    def add_menu_item(self):
        name = self.entry_name.get().strip()
        price = self.entry_price.get().strip()
        description = self.entry_description.get().strip()
        if name and price.isdigit() and description:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            existing = DatabaseManager.fetch_all("SELECT timestamp FROM menu WHERE name = ?", (name,))
            if existing:
                existing_timestamp = existing[0][0]
                if timestamp > existing_timestamp:
                    DatabaseManager.execute("DELETE FROM menu WHERE name = ?", (name,))
            DatabaseManager.execute("INSERT INTO menu (name, price, description, timestamp) VALUES (?, ?, ?, ?)", (name, int(price), description, timestamp))
            self.refresh_list()
            self.clear_entries()
            messagebox.showinfo("Success", "Menu item added/updated.")
        else:
            messagebox.showwarning("Warning", "Please fill in all fields with valid data.")

    def delete_menu_item(self):
        selected = self.tree.selection()
        if selected:
            item_value = self.tree.item(selected[0], "values")[0]
            DatabaseManager.execute("DELETE FROM menu WHERE name = ?", (item_value,))
            self.refresh_list()
            messagebox.showinfo("Success", "Item deleted successfully.")
        else:
            messagebox.showwarning("Warning", "Please select an item.")

    def refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        data = DatabaseManager.fetch_all("SELECT name, price || ' Toman', description, timestamp FROM menu")
        for record in data:
            self.tree.insert("", tk.END, values=record)

    def clear_entries(self):
        self.entry_name.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.entry_description.delete(0, tk.END)

class ParseTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(self.frame, text="Enter the text to parse:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.text_input = scrolledtext.ScrolledText(self.frame, width=80, height=15, font=("Helvetica", 9))
        self.text_input.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        ttk.Button(self.frame, text="Parse and Save/Update", command=self.parse_and_save, style="Small.TButton", width=15).grid(row=2, column=0, pady=5, sticky="ew")

        # Configure grid weights to make the text area expand
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

    def parse_and_save(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter text.")
            return

        pattern = r"(.+?)\n(.+?)\n(\d{1,3}(?:,\d{3})*) تومان"
        matches = re.findall(pattern, text)
        if not matches:
            messagebox.showwarning("Warning", "No valid menu items found.")
            return

        for name, description, price in matches:
            price = int(price.replace(",", ""))
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            DatabaseManager.execute(
                "INSERT OR REPLACE INTO menu (name, price, description, timestamp) VALUES (?, ?, ?, ?)",
                (name.strip(), price, description.strip(), timestamp),
            )
        messagebox.showinfo("Success", "Menu items parsed and saved/updated.")

class RestaurantManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Management System")
        self.root.geometry("800x600")

        # Define a custom style for smaller buttons
        self.style = ttk.Style()
        self.style.configure("Small.TButton", font=("Helvetica", 9), padding=3)

        self.tab_control = ttk.Notebook(self.root)
        self.tab_qa = ttk.Frame(self.tab_control)
        self.tab_menu = ttk.Frame(self.tab_control)
        self.tab_parse = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab_qa, text="Manage Q&A")
        self.tab_control.add(self.tab_menu, text="Manage Menu")
        self.tab_control.add(self.tab_parse, text="Parse Text")
        self.tab_control.pack(fill="both", expand=True)

        self.qa_tab = QATab(self.tab_qa)
        self.menu_tab = MenuTab(self.tab_menu)
        self.parse_tab = ParseTab(self.tab_parse)

if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantManagementApp(root)
    root.mainloop()