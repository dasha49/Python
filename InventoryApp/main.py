import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from product import Product
from csv_storage import CSVStorage


class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Облік товарів")
        self.root.geometry("1100x680")
        self.root.minsize(900, 560)

        self.storage = CSVStorage()
        self.products = []
        self.selected_id = None
        self.file_path = str(Path(__file__).with_name("inventory.csv"))

        self._build_ui()
        self.load_file(self.file_path, show_message=False)
        self.refresh_table()

    def _build_ui(self):
        # Меню
        menu = tk.Menu(self.root)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Відкрити CSV...", command=self.open_file)
        file_menu.add_command(label="Зберегти", command=self.save_file)
        file_menu.add_command(label="Зберегти як...", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Вихід", command=self.root.destroy)
        menu.add_cascade(label="Файл", menu=file_menu)
        self.root.config(menu=menu)

        # Пошук
        search_frame = ttk.Frame(self.root, padding=(12, 10))
        search_frame.pack(fill="x")
        ttk.Label(search_frame, text="Пошук (назва / категорія):").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=35)
        search_entry.pack(side="left", padx=8)
        search_entry.bind("<KeyRelease>", lambda _event: self.refresh_table())
        ttk.Button(search_frame, text="Очистити пошук",
                   command=lambda: self.search_var.set("")).pack(side="left")

        # Таблиця
        table_frame = ttk.Frame(self.root, padding=(12, 0))
        table_frame.pack(fill="both", expand=True)
        columns = ("id", "name", "category", "quantity", "price", "location")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                 selectmode="browse")
        headings = {
            "id": ("ID", 60), "name": ("Назва", 240),
            "category": ("Категорія", 160), "quantity": ("Кількість", 100),
            "price": ("Ціна", 110), "location": ("Склад / полиця", 180)
        }
        for col, (label, width) in headings.items():
            self.tree.heading(col, text=label,
                              command=lambda c=col: self.sort_by(c))
            self.tree.column(col, width=width, anchor="center" if col in ("id", "quantity", "price") else "w")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Форма
        form = ttk.LabelFrame(self.root, text="Дані товару", padding=12)
        form.pack(fill="x", padx=12, pady=10)
        self.vars = {key: tk.StringVar() for key in
                     ("name", "category", "quantity", "price", "location")}
        labels = [("name", "Назва"), ("category", "Категорія"),
                  ("quantity", "Кількість"), ("price", "Ціна"),
                  ("location", "Склад / полиця")]
        for index, (key, label) in enumerate(labels):
            row, col = divmod(index, 3)
            ttk.Label(form, text=label).grid(row=row*2, column=col, sticky="w", padx=6)
            ttk.Entry(form, textvariable=self.vars[key], width=30).grid(
                row=row*2+1, column=col, sticky="ew", padx=6, pady=(2,8))
            form.columnconfigure(col, weight=1)

        buttons = ttk.Frame(self.root, padding=(12, 0, 12, 10))
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Додати", command=self.add_product).pack(side="left", padx=4)
        ttk.Button(buttons, text="Оновити вибраний", command=self.update_product).pack(side="left", padx=4)
        ttk.Button(buttons, text="Видалити вибраний", command=self.delete_product).pack(side="left", padx=4)
        ttk.Button(buttons, text="Очистити форму", command=self.clear_form).pack(side="left", padx=4)

        # Status bar
        self.status_var = tk.StringVar(value="Готово.")
        status = ttk.Label(self.root, textvariable=self.status_var, relief="sunken",
                           anchor="w", padding=(8, 4))
        status.pack(side="bottom", fill="x")

    def set_status(self, message):
        self.status_var.set(message)

    def validate_form(self):
        name = self.vars["name"].get().strip()
        category = self.vars["category"].get().strip()
        quantity_text = self.vars["quantity"].get().strip()
        price_text = self.vars["price"].get().strip().replace(",", ".")
        location = self.vars["location"].get().strip()

        if not name or not category:
            raise ValueError("Назва та категорія не можуть бути порожніми.")
        if not quantity_text:
            raise ValueError("Введіть кількість.")
        try:
            quantity = int(quantity_text)
        except ValueError:
            raise ValueError("Кількість має бути цілим числом.")
        if quantity < 0:
            raise ValueError("Кількість не може бути від’ємною.")
        if not price_text:
            raise ValueError("Введіть ціну.")
        try:
            price = float(price_text)
        except ValueError:
            raise ValueError("Ціна має бути числом (наприклад, 12.50 або 12,50).")
        if price < 0:
            raise ValueError("Ціна не може бути від’ємною.")
        return name, category, quantity, price, location

    def next_id(self):
        return max((p.id for p in self.products), default=0) + 1

    def add_product(self):
        try:
            name, category, quantity, price, location = self.validate_form()
            product = Product(self.next_id(), name, category, quantity, price, location)
            self.products.append(product)
            self.refresh_table()
            self.clear_form()
            self.set_status(f"Товар «{name}» додано.")
        except ValueError as error:
            self.set_status(f"Помилка: {error}")
            messagebox.showerror("Перевірка даних", str(error))

    def update_product(self):
        if self.selected_id is None:
            messagebox.showwarning("Увага", "Спочатку виберіть товар у таблиці.")
            return
        try:
            name, category, quantity, price, location = self.validate_form()
            product = self.find_product(self.selected_id)
            product.name, product.category = name, category
            product.quantity, product.price = quantity, price
            product.location = location
            self.refresh_table()
            self.set_status(f"Товар ID {product.id} оновлено.")
        except ValueError as error:
            self.set_status(f"Помилка: {error}")
            messagebox.showerror("Перевірка даних", str(error))

    def delete_product(self):
        if self.selected_id is None:
            messagebox.showwarning("Увага", "Спочатку виберіть товар у таблиці.")
            return
        product = self.find_product(self.selected_id)
        if messagebox.askyesno("Підтвердження", f"Видалити товар «{product.name}»?"):
            self.products = [p for p in self.products if p.id != self.selected_id]
            self.clear_form()
            self.refresh_table()
            self.set_status(f"Товар ID {product.id} видалено.")

    def clear_form(self):
        for variable in self.vars.values():
            variable.set("")
        self.selected_id = None
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def find_product(self, product_id):
        return next(p for p in self.products if p.id == product_id)

    def on_select(self, _event=None):
        selected = self.tree.selection()
        if not selected:
            return
        product_id = int(selected[0])
        product = self.find_product(product_id)
        self.selected_id = product_id
        for key in self.vars:
            self.vars[key].set(str(getattr(product, key)))
        self.set_status(f"Вибрано товар ID {product_id}.")

    def refresh_table(self):
        query = self.search_var.get().strip().casefold()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for product in self.products:
            if query and query not in product.name.casefold() and query not in product.category.casefold():
                continue
            self.tree.insert("", "end", iid=str(product.id), values=(
                product.id, product.name, product.category, product.quantity,
                f"{product.price:.2f}", product.location
            ))
        self.set_status(f"Записів: {len(self.products)} | Показано: {len(self.tree.get_children())}")

    def sort_by(self, column):
        items = [(self.tree.set(item, column), item) for item in self.tree.get_children()]
        reverse = getattr(self, "_sort_reverse", {}).get(column, False)
        def key(pair):
            value = pair[0]
            try:
                return float(value)
            except ValueError:
                return value.casefold()
        items.sort(key=key, reverse=reverse)
        for index, (_, item) in enumerate(items):
            self.tree.move(item, "", index)
        if not hasattr(self, "_sort_reverse"):
            self._sort_reverse = {}
        self._sort_reverse[column] = not reverse

    def load_file(self, path, show_message=True):
        try:
            loaded = self.storage.load(path)
            self.products = loaded
            self.file_path = str(path)
            self.refresh_table()
            self.set_status(f"Завантажено {len(loaded)} товарів.")
            if show_message:
                messagebox.showinfo("CSV", f"Завантажено записів: {len(loaded)}")
        except (OSError, ValueError) as error:
            messagebox.showerror("Помилка відкриття", str(error))
            self.set_status(f"Не вдалося відкрити файл: {error}")

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Відкрити CSV", filetypes=[("CSV файли", "*.csv"), ("Усі файли", "*.*")]
        )
        if path:
            self.load_file(path)

    def save_file(self):
        try:
            self.storage.save(self.file_path, self.products)
            self.set_status(f"Збережено {len(self.products)} товарів у {self.file_path}")
            messagebox.showinfo("Збереження", "Дані успішно збережено.")
        except OSError as error:
            messagebox.showerror("Помилка збереження", str(error))

    def save_as(self):
        path = filedialog.asksaveasfilename(
            title="Зберегти CSV як", defaultextension=".csv",
            filetypes=[("CSV файли", "*.csv")]
        )
        if path:
            self.file_path = path
            self.save_file()


if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
