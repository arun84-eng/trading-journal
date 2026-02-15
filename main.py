# main.py
# Trading Journal Desktop App using Tkinter + SQLite

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from tkinter import simpledialog
import sqlite3
import os
import datetime
import csv
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Ensure images directory exists
os.makedirs("images", exist_ok=True)

# Database setup
DB_PATH = "journal.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            pair TEXT,
            direction TEXT,
            quantity REAL,
            strategy TEXT,
            waited_4h INTEGER,
            trend_followed INTEGER,
            rr_ok INTEGER,
            emotional INTEGER,
            followed_plan INTEGER,
            profit_percent REAL,
            notes TEXT,
            pre_image_path TEXT,
            post_image_path TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Global checklist rules (easily editable)
RULES = [
    ("waited_4h", "Waited for 4H candle close"),
    ("trend_followed", "Followed trend"),
    ("rr_ok", "Proper risk-reward"),
    ("emotional", "No emotional entry"),
    ("followed_plan", "Entry matched plan")
]

# -------------------------- MAIN APP --------------------------

class TradingJournalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Trading Journal")
        self.geometry("1000x700")
        self.minsize(900, 600)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Add tabs
        self.add_trade_tab = ttk.Frame(self.notebook)
        self.history_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.add_trade_tab, text="Add Trade")
        self.notebook.add(self.history_tab, text="History")
        self.notebook.add(self.stats_tab, text="Statistics")

        self.create_add_trade_tab()
        self.create_history_tab()
        self.create_statistics_tab()

    # -------------------------- ADD TRADE TAB --------------------------

    def create_add_trade_tab(self):
        frame = self.add_trade_tab
        row = 0

        # Date
        tk.Label(frame, text="Date:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.date_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(frame, textvariable=self.date_var, width=20).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1

        # Pair
        tk.Label(frame, text="Trading Pair / Instrument:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.pair_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.pair_var, width=20).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1

        # Direction
        tk.Label(frame, text="Trade Type:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.direction_var = tk.StringVar(value="Buy")
        tk.OptionMenu(frame, self.direction_var, "Buy", "Sell").grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1

        # Quantity
        tk.Label(frame, text="Quantity / Lot Size:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.quantity_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.quantity_var, width=20).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1

        # Strategy
        tk.Label(frame, text="Strategy Name:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.strategy_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.strategy_var, width=20).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1

        # Checklist
        tk.Label(frame, text="Checklist:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", padx=5, pady=3)
        row += 1

        self.check_vars = {}
        for key, label in RULES:
            var = tk.IntVar(value=0)
            tk.Checkbutton(frame, text=label, variable=var).grid(row=row, column=0, sticky="w", padx=10, pady=2)
            self.check_vars[key] = var
            row += 1

        # Result
        tk.Label(frame, text="Profit/Loss %:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.profit_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.profit_var, width=20).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1

        tk.Label(frame, text="Risk–Reward Achieved:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.rr_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.rr_var, width=20).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1

        tk.Label(frame, text="Notes:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.notes_text = scrolledtext.ScrolledText(frame, width=40, height=4)
        self.notes_text.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1

        # Image uploads
        tk.Label(frame, text="Pre-Trade Screenshot:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.pre_image_path = tk.StringVar()
        tk.Button(frame, text="Upload", command=lambda: self.upload_image(self.pre_image_path)).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1

        tk.Label(frame, text="Post-Trade Screenshot:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
        self.post_image_path = tk.StringVar()
        tk.Button(frame, text="Upload", command=lambda: self.upload_image(self.post_image_path)).grid(row=row, column=1, sticky="w", padx=5, pady=3)
        row += 1

        # Save button
        tk.Button(frame, text="Save Trade", bg="green", fg="white", font=("Arial", 11, "bold"),
                  command=self.save_trade).grid(row=row, column=0, columnspan=2, pady=15)

    def upload_image(self, path_var):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
        if file_path:
            # Copy image to /images folder
            filename = os.path.basename(file_path)
            new_path = os.path.join("images", filename)
            try:
                img = Image.open(file_path)
                img.save(new_path)
                path_var.set(new_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save image: {e}")

    def save_trade(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO trades (
                    date, pair, direction, quantity, strategy,
                    waited_4h, trend_followed, rr_ok, emotional, followed_plan,
                    profit_percent, notes, pre_image_path, post_image_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.date_var.get(),
                self.pair_var.get(),
                self.direction_var.get(),
                float(self.quantity_var.get() or 0),
                self.strategy_var.get(),
                self.check_vars["waited_4h"].get(),
                self.check_vars["trend_followed"].get(),
                self.check_vars["rr_ok"].get(),
                self.check_vars["emotional"].get(),
                self.check_vars["followed_plan"].get(),
                float(self.profit_var.get() or 0),
                self.notes_text.get("1.0", "end-1c"),
                self.pre_image_path.get(),
                self.post_image_path.get()
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Trade saved successfully!")
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save trade: {e}")

    def clear_form(self):
        self.pair_var.set("")
        self.quantity_var.set("")
        self.strategy_var.set("")
        self.profit_var.set("")
        self.rr_var.set("")
        self.notes_text.delete("1.0", "end")
        self.pre_image_path.set("")
        self.post_image_path.set("")
        for var in self.check_vars.values():
            var.set(0)

    # -------------------------- HISTORY TAB --------------------------

    def create_history_tab(self):
        frame = self.history_tab

        # Filters
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(pady=5, padx=5, anchor="w")

        tk.Label(filter_frame, text="Filter:").pack(side="left", padx=3)
        self.filter_var = tk.StringVar(value="All")
        tk.OptionMenu(filter_frame, self.filter_var, "All", "Winning", "Losing", "By Strategy", command=self.load_history).pack(side="left", padx=3)

        self.strategy_filter_var = tk.StringVar()
        tk.Entry(filter_frame, textvariable=self.strategy_filter_var, width=15).pack(side="left", padx=3)
        tk.Button(filter_frame, text="Apply", command=self.load_history).pack(side="left", padx=3)

        tk.Button(filter_frame, text="Export CSV", command=self.export_csv).pack(side="left", padx=10)

        # Treeview
        self.history_tree = ttk.Treeview(frame, columns=(
            "id", "date", "pair", "direction", "profit", "winloss", "strategy"
        ), show="headings")

        for col, text in zip(
            ("id", "date", "pair", "direction", "profit", "winloss", "strategy"),
            ("ID", "Date", "Pair", "Type", "P/L %", "Win/Loss", "Strategy")
        ):
            self.history_tree.heading(col, text=text)
            self.history_tree.column(col, width=80)

        self.history_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Bind double click
        self.history_tree.bind("<Double-1>", self.view_trade_details)

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Edit Selected", bg="orange", fg="white", command=self.edit_selected_trade).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete Selected", bg="red", fg="white", command=self.delete_selected_trade).pack(side="left", padx=5)

        self.load_history()

    def load_history(self, *args):
        for i in self.history_tree.get_children():
            self.history_tree.delete(i)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trades")
        trades = cursor.fetchall()
        conn.close()

        filter_type = self.filter_var.get()
        strategy_filter = self.strategy_filter_var.get().strip().lower()

        for trade in trades:
            pid, date, pair, direction, qty, strategy, w4h, trend, rr, emotional, followed, profit, notes, pre, post = trade

            if filter_type == "Winning" and profit <= 0: continue
            if filter_type == "Losing" and profit >= 0: continue
            if strategy_filter and strategy.lower().find(strategy_filter) == -1: continue

            winloss = "Win" if profit > 0 else "Loss" if profit < 0 else "Breakeven"
            color = "green" if profit > 0 else "red" if profit < 0 else "gray"

            item = self.history_tree.insert("", "end", values=(
                pid, date, pair, direction, f"{profit:.2f}%", winloss, strategy
            ))
            self.history_tree.tag_configure(item, foreground=color)

    def view_trade_details(self, event):
        selected = self.history_tree.selection()
        if not selected:
            return
        item = self.history_tree.item(selected[0])
        pid = item["values"][0]
        self.open_trade_detail_window(pid)

    def open_trade_detail_window(self, pid):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trades WHERE id=?", (pid,))
        trade = cursor.fetchone()
        conn.close()

        if not trade:
            return

        detail = tk.Toplevel(self)
        detail.title(f"Trade #{pid} Details")
        detail.geometry("700x500")

        labels = [
            ("Date", trade[1]), ("Pair", trade[2]), ("Direction", trade[3]),
            ("Quantity", trade[4]), ("Strategy", trade[5]),
            ("Profit/Loss %", f"{trade[11]:.2f}%"), ("Notes", trade[12])
        ]

        row = 0
        for label, value in labels:
            tk.Label(detail, text=f"{label}:").grid(row=row, column=0, sticky="w", padx=5, pady=3)
            tk.Label(detail, text=str(value)).grid(row=row, column=1, sticky="w", padx=5, pady=3)
            row += 1

        # Checklist
        tk.Label(detail, text="Checklist:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", padx=5, pady=3)
        row += 1
        bools = [trade[6], trade[7], trade[8], trade[9], trade[10]]
        for key, label in RULES:
            status = "✓" if bools[[r[0] for r in RULES].index(key)] else "✗"
            tk.Label(detail, text=f"{label}: {status}").grid(row=row, column=0, sticky="w", padx=10, pady=2)
            row += 1

        # Images
        def show_image(path, label):
            if path and os.path.exists(path):
                img = Image.open(path)
                img = img.resize((250, 150))
                photo = ImageTk.PhotoImage(img)
                tk.Label(detail, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=3)
                lbl = tk.Label(detail, image=photo)
                lbl.image = photo
                lbl.grid(row=row, column=1, sticky="w", padx=5, pady=3)
                row += 1

        show_image(trade[13], "Pre-Trade Screenshot:")
        show_image(trade[14], "Post-Trade Screenshot:")

    def edit_selected_trade(self):
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showwarning("Edit", "No trade selected.")
            return

        item = self.history_tree.item(selected[0])
        pid = item["values"][0]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trades WHERE id=?", (pid,))
        trade = cursor.fetchone()
        conn.close()

        if not trade:
            return

        # Open edit window
        edit_win = tk.Toplevel(self)
        edit_win.title(f"Edit Trade #{pid}")
        edit_win.geometry("500x400")

        # Basic fields
        fields = [
            ("Date", tk.StringVar(value=trade[1])),
            ("Pair", tk.StringVar(value=trade[2])),
            ("Direction", tk.StringVar(value=trade[3])),
            ("Quantity", tk.StringVar(value=str(trade[4]))),
            ("Strategy", tk.StringVar(value=trade[5])),
            ("Profit %", tk.StringVar(value=str(trade[11]))),
            ("Risk–Reward", tk.StringVar(value="")),
            ("Notes", tk.StringVar(value=trade[12])),
        ]

        row = 0
        for label, var in fields:
            tk.Label(edit_win, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=3)
            if label == "Notes":
                txt = scrolledtext.ScrolledText(edit_win, width=40, height=4)
                txt.grid(row=row, column=1, sticky="w", padx=5, pady=3)
                txt.insert("1.0", trade[12])
                fields[row] = (label, txt)
            else:
                tk.Entry(edit_win, textvariable=var, width=20).grid(row=row, column=1, sticky="w", padx=5, pady=3)
            row += 1

        # Save edit
        def save_edit():
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE trades SET
                    date=?, pair=?, direction=?, quantity=?, strategy=?,
                    profit_percent=?, notes=?
                    WHERE id=?
                """, (
                    fields[0][1].get(), fields[1][1].get(), fields[2][1].get(),
                    float(fields[3][1].get() or 0), fields[4][1].get(),
                    float(fields[5][1].get() or 0),
                    fields[7][1].get("1.0", "end-1c"),
                    pid
                ))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Trade updated.")
                edit_win.destroy()
                self.load_history()
            except Exception as e:
                messagebox.showerror("Error", f"Could not update trade: {e}")

        tk.Button(edit_win, text="Save Changes", bg="green", fg="white", command=save_edit).grid(row=row, column=0, columnspan=2, pady=10)

    def delete_selected_trade(self):
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showwarning("Delete", "No trade selected.")
            return

        item = self.history_tree.item(selected[0])
        pid = item["values"][0]

        if messagebox.askyesno("Confirm Delete", "Delete this trade permanently?"):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM trades WHERE id=?", (pid,))
            conn.commit()
            conn.close()
            self.load_history()

    # -------------------------- STATISTICS TAB --------------------------

    def create_statistics_tab(self):
        frame = self.stats_tab

        self.stats_labels = {}

        # Summary labels
        summary_frame = ttk.Frame(frame)
        summary_frame.pack(pady=10, anchor="w", padx=10)

        metrics = ["Total Trades", "Win Rate", "Avg Win %", "Avg Loss %", "Most Broken Rule"]
        for i, metric in enumerate(metrics):
            tk.Label(summary_frame, text=f"{metric}:", font=("Arial", 10, "bold")).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            self.stats_labels[metric] = tk.Label(summary_frame, text="")
            self.stats_labels[metric].grid(row=i, column=1, sticky="w", padx=10, pady=3)

        # Equity Curve
        self.fig, self.ax = plt.subplots(figsize=(6, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        self.update_stats()

    def update_stats(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trades")
        trades = cursor.fetchall()
        conn.close()

        total = len(trades)
        wins = sum(1 for t in trades if t[11] > 0)
        losses = sum(1 for t in trades if t[11] < 0)

        win_rate = (wins / total * 100) if total else 0
        avg_win = (sum(t[11] for t in trades if t[11] > 0) / wins) if wins else 0
        avg_loss = (sum(t[11] for t in trades if t[11] < 0) / losses) if losses else 0

        # Most broken rule
        rule_counts = [0, 0, 0, 0, 0]
        for t in trades:
            rule_counts[0] += t[6]
            rule_counts[1] += t[7]
            rule_counts[2] += t[8]
            rule_counts[3] += t[9]
            rule_counts[4] += t[10]

        most_broken = RULES[rule_counts.index(max(rule_counts))][1]

        # Update labels
        self.stats_labels["Total Trades"].config(text=str(total))
        self.stats_labels["Win Rate"].config(text=f"{win_rate:.1f}%")
        self.stats_labels["Avg Win %"].config(text=f"{avg_win:.2f}%")
        self.stats_labels["Avg Loss %"].config(text=f"{avg_loss:.2f}%")
        self.stats_labels["Most Broken Rule"].config(text=most_broken)

        # Equity curve
        self.ax.clear()
        equity = 0
        x, y = [], []
        for t in trades:
            equity += t[11]
            x.append(t[1])
            y.append(equity)
        self.ax.plot(x, y, marker="o")
        self.ax.set_title("Equity Curve")
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Cumulative P/L %")
        self.fig.autofmt_xdate()
        self.canvas.draw()

    # -------------------------- CSV EXPORT --------------------------

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trades")
        rows = cursor.fetchall()
        conn.close()

        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ID", "Date", "Pair", "Direction", "Quantity", "Strategy",
                "Waited 4H", "Trend Followed", "RR OK", "Emotional", "Followed Plan",
                "Profit%", "Notes", "Pre Image", "Post Image"
            ])
            for row in rows:
                writer.writerow(row)

        messagebox.showinfo("Export", f"Exported {len(rows)} trades to {path}")

# -------------------------- RUN APP --------------------------

if __name__ == "__main__":
    app = TradingJournalApp()
    app.mainloop()