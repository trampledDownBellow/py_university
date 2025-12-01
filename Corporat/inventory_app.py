import csv
import os
import sys
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
COLUMNS = (
    "id",
    "name",
    "category",
    "quantity",
    "price",
    "location",
    "created_at",
)

class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Облік товарів")
        self.geometry("980x520")
        self.minsize(900, 480)
        self.items = []
        self.filtered_items = []
        self.current_file = None
        self.sort_state = {}
        self.create_styles()
        self.create_menu()
        self.create_widgets()
        self.bind_events()
        self.update_status("Готово")

    def create_styles(self):
        style = ttk.Style(self)
        style.configure("Invalid.TEntry", fieldbackground="#ffd6d6")

    def create_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Відкрити…", command=self.load_csv)
        file_menu.add_command(label="Зберегти", command=self.save_csv)
        file_menu.add_command(label="Зберегти як…", command=lambda: self.save_csv(save_as=True))
        file_menu.add_separator()
        file_menu.add_command(label="Вихід", command=self.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        self.config(menu=menubar)

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(search_frame, text="Пошук (назва/категорія):").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        search_entry.bind("<KeyRelease>", lambda _e: self.apply_filter())

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        table_frame = ttk.Frame(content_frame)
        table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(
            table_frame,
            columns=COLUMNS,
            show="headings",
            selectmode="browse",
        )
        for col in COLUMNS:
            heading_text = col.replace("_", " ").title()
            self.tree.heading(col, text=heading_text, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, anchor=tk.W, stretch=True, width=110)
        self.tree.column("name", width=160)
        self.tree.column("category", width=140)
        self.tree.column("price", width=100, anchor=tk.E)
        self.tree.column("quantity", width=90, anchor=tk.E)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        form_frame = ttk.LabelFrame(content_frame, text="Дані товару", padding=10)
        form_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        self.entries = {}
        form_fields = [
            ("id", "ID"),
            ("name", "Назва"),
            ("category", "Категорія"),
            ("quantity", "Кількість"),
            ("price", "Ціна"),
            ("location", "Розташування"),
        ]
        for i, (field, label) in enumerate(form_fields):
            ttk.Label(form_frame, text=label + ":").grid(row=i, column=0, sticky=tk.W, pady=4, padx=(0, 8))
            entry = ttk.Entry(form_frame)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=4)
            form_frame.columnconfigure(1, weight=1)
            self.entries[field] = entry

        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=len(form_fields), column=0, columnspan=2, pady=(12, 0), sticky=tk.EW)
        button_frame.columnconfigure((0, 1), weight=1)
        ttk.Button(button_frame, text="Додати", command=self.add_item).grid(row=0, column=0, sticky=tk.EW, padx=(0, 4))
        ttk.Button(button_frame, text="Оновити", command=self.update_item).grid(row=0, column=1, sticky=tk.EW, padx=(4, 0))
        ttk.Button(button_frame, text="Видалити", command=self.delete_item).grid(row=1, column=0, sticky=tk.EW, padx=(0, 4), pady=(6, 0))
        ttk.Button(button_frame, text="Очистити форму", command=self.clear_form).grid(row=1, column=1, sticky=tk.EW, padx=(4, 0), pady=(6, 0))

        self.status_var = tk.StringVar(value="Готово")
        status_bar = ttk.Label(self, textvariable=self.status_var, anchor=tk.W, padding=(10, 4))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def bind_events(self):
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.bind("<Control-s>", lambda _e: self.save_csv())
        self.bind("<Control-o>", lambda _e: self.load_csv())

    def apply_filter(self):
        query = self.search_var.get().lower().strip()
        if not query:
            self.filtered_items = list(self.items)
        else:
            self.filtered_items = [
                item
                for item in self.items
                if query in item["name"].lower() or query in item["category"].lower()
            ]
        self.refresh_tree()
        self.update_status(f"Знайдено записів: {len(self.filtered_items)}")

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for item in self.filtered_items:
            values = (item["id"], item["name"], item["category"], item["quantity"], f"{item['price']:.2f}", item["location"], item["created_at"])
            self.tree.insert("", tk.END, values=values)

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
            entry.configure(style="TEntry")
        self.update_status("Форма очищена")

    def on_tree_select(self, _event=None):
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0], "values")
        field_order = ["id", "name", "category", "quantity", "price", "location"]
        for value, field in zip(values, field_order):
            self.entries[field].delete(0, tk.END)
            self.entries[field].insert(0, value)
        self.update_status("Завантажено запис у форму")

    def validate_form(self, require_unique_id=True):
        errors = []
        data = {}
        id_value = self.entries["id"].get().strip()
        if not id_value:
            id_value = self.generate_id()
        elif require_unique_id and any(item["id"] == id_value for item in self.items):
            errors.append(("id", "ID має бути унікальним"))
        data["id"] = id_value

        name = self.entries["name"].get().strip()
        if not name:
            errors.append(("name", "Назва не може бути порожньою"))
        data["name"] = name
        category = self.entries["category"].get().strip()
        if not category:
            errors.append(("category", "Категорія не може бути порожньою"))
        data["category"] = category
        quantity_raw = self.entries["quantity"].get().strip()
        try:
            quantity = int(quantity_raw)
            if quantity < 0:
                raise ValueError
        except ValueError:
            errors.append(("quantity", "Кількість має бути цілим числом ≥ 0"))
            quantity = 0
        data["quantity"] = quantity
        price_raw = self.entries["price"].get().strip().replace(",", ".")
        try:
            price = float(price_raw)
            if price < 0:
                raise ValueError
        except ValueError:
            errors.append(("price", "Ціна має бути числом ≥ 0"))
            price = 0.0
        data["price"] = price
        location = self.entries["location"].get().strip()
        data["location"] = location

        for entry in self.entries.values():
            entry.configure(style="TEntry")
        if errors:
            for field, msg in errors:
                self.entries[field].configure(style="Invalid.TEntry")
            self.update_status(errors[0][1])
            return None
        return data

    def generate_id(self):
        existing_ids = {item["id"] for item in self.items}
        base = len(self.items) + 1
        new_id = str(base)
        while new_id in existing_ids:
            base += 1
            new_id = str(base)
        return new_id

    def add_item(self):
        validated = self.validate_form(require_unique_id=True)
        if not validated:
            return
        validated["created_at"] = datetime.now().strftime(DATE_FORMAT)
        self.items.append(validated)
        self.apply_filter()
        self.clear_form()
        self.update_status("Запис додано")

    def get_selected_item_index(self):
        selection = self.tree.selection()
        if not selection:
            return None
        selected_id = self.tree.item(selection[0], "values")[0]
        for idx, item in enumerate(self.items):
            if item["id"] == selected_id:
                return idx
        return None

    def update_item(self):
        index = self.get_selected_item_index()
        if index is None:
            self.update_status("Оберіть запис для оновлення")
            messagebox.showinfo("Оновлення", "Будь ласка, виберіть запис у таблиці")
            return
        validated = self.validate_form(require_unique_id=False)
        if not validated:
            return
        selected_id = self.items[index]["id"]
        if validated["id"] != selected_id and any(item["id"] == validated["id"] for item in self.items):
            self.entries["id"].configure(style="Invalid.TEntry")
            self.update_status("ID має бути унікальним")
            return

        validated["created_at"] = self.items[index]["created_at"]
        self.items[index] = validated
        self.apply_filter()
        self.update_status("Запис оновлено")

    def delete_item(self):
        index = self.get_selected_item_index()
        if index is None:
            self.update_status("Оберіть запис для видалення")
            messagebox.showinfo("Видалення", "Будь ласка, виберіть запис у таблиці")
            return
        confirm = messagebox.askyesno("Підтвердження", "Видалити вибраний запис?")
        if not confirm:
            return
        del self.items[index]
        self.apply_filter()
        self.clear_form()
        self.update_status("Запис видалено")

    def load_csv(self):
        path = filedialog.askopenfilename(
            title="Відкрити CSV",
            filetypes=(("CSV файли", "*.csv"), ("Усі файли", "*.*")),
        )
        if not path:
            return
        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames is None or [h.strip() for h in reader.fieldnames] != list(COLUMNS):
                    raise ValueError("Неправильні заголовки CSV")
                loaded_items = []
                for row in reader:
                    try:
                        loaded_items.append(
                            {
                                "id": row["id"],
                                "name": row["name"],
                                "category": row["category"],
                                "quantity": int(row["quantity"]),
                                "price": float(row["price"]),
                                "location": row.get("location", ""),
                                "created_at": row.get("created_at", ""),
                            }
                        )
                    except (TypeError, ValueError, KeyError):
                        raise ValueError("Неправильний формат даних у CSV")
        except Exception as exc:
            messagebox.showerror("Помилка", f"Не вдалося завантажити файл:\n{exc}")
            self.update_status("Помилка завантаження CSV")
            return
        self.items = loaded_items
        self.filtered_items = list(self.items)
        self.refresh_tree()
        self.current_file = path
        self.update_status(f"Завантажено {len(self.items)} записів")

    def save_csv(self, save_as=False):
        if save_as or not self.current_file:
            path = filedialog.asksaveasfilename(
                title="Зберегти CSV",
                defaultextension=".csv",
                filetypes=(("CSV файли", "*.csv"), ("Усі файли", "*.*")),
            )
            if not path:
                return
            self.current_file = path
        try:
            with open(self.current_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=COLUMNS)
                writer.writeheader()
                for item in self.items:
                    writer.writerow(item)
        except OSError as exc:
            messagebox.showerror("Помилка", f"Не вдалося зберегти файл:\n{exc}")
            self.update_status("Помилка збереження CSV")
            return

        self.update_status(f"Збережено {len(self.items)} записів у {os.path.basename(self.current_file)}")

    def sort_by_column(self, column):
        reverse = self.sort_state.get(column, False)
        try:
            if column in {"quantity", "price"}:
                key_func = lambda item: float(item[column])
            else:
                key_func = lambda item: item[column]
            self.filtered_items.sort(key=key_func, reverse=reverse)
            self.sort_state[column] = not reverse
            self.refresh_tree()
            direction = "спадання" if reverse else "зростання"
            self.update_status(f"Сортування за '{column}' ({direction})")
        except Exception:
            self.update_status("Не вдалося відсортувати")

    def update_status(self, text):
        self.status_var.set(text)

def main():
    app = InventoryApp()
    app.mainloop()

if __name__ == "__main__":
    main()