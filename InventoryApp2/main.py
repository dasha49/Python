
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from product import Product
from api_client import InventoryAPI


class InventoryApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Облік товарів")
        self.root.geometry("1100x680")
        self.root.minsize(900, 560)

        # Підключення до API
        self.api = InventoryAPI()

        self.products = []
        self.selected_id = None

        # Створення інтерфейсу
        self._build_ui()

        # Завантаження товарів із сервера або кешу
        self.load_products()

    # ---------- INTERFACE ----------

    def _build_ui(self):

        # Меню
        menu = tk.Menu(self.root)

        file_menu = tk.Menu(menu, tearoff=0)

        file_menu.add_command(
            label="Синхронізувати зараз",
            command=self.synchronize
        )

        file_menu.add_command(
            label="Експорт CSV",
            command=self.export_csv
        )

        file_menu.add_separator()

        file_menu.add_command(
            label="Вихід",
            command=self.root.destroy
        )

        menu.add_cascade(label="Файл", menu=file_menu)

        self.root.config(menu=menu)

        # Пошук
        search_frame = ttk.Frame(self.root, padding=(12, 10))
        search_frame.pack(fill="x")

        ttk.Label(
            search_frame,
            text="Пошук (назва / категорія):"
        ).pack(side="left")

        self.search_var = tk.StringVar()

        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=35
        )

        search_entry.pack(side="left", padx=8)

        search_entry.bind(
            "<KeyRelease>",
            lambda event: self.refresh_table()
        )

        ttk.Button(
            search_frame,
            text="Очистити пошук",
            command=lambda: self.search_var.set("")
        ).pack(side="left")

        # Таблиця товарів
        table_frame = ttk.Frame(self.root, padding=(12, 0))
        table_frame.pack(fill="both", expand=True)

        columns = (
            "id", "name", "category",
            "quantity", "price", "location"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headings = {
            "id": ("ID", 100),
            "name": ("Назва", 240),
            "category": ("Категорія", 160),
            "quantity": ("Кількість", 100),
            "price": ("Ціна", 110),
            "location": ("Склад / полиця", 180)
        }

        for col, (label, width) in headings.items():

            self.tree.heading(
                col,
                text=label,
                command=lambda c=col: self.sort_by(c)
            )

            self.tree.column(
                col,
                width=width,
                anchor="center" if col in ("id", "quantity", "price") else "w"
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.on_select
        )

        # Форма товару
        form = ttk.LabelFrame(
            self.root,
            text="Дані товару",
            padding=12
        )

        form.pack(fill="x", padx=12, pady=10)

        self.vars = {
            key: tk.StringVar()
            for key in (
                "name", "category", "quantity",
                "price", "location"
            )
        }

        labels = [
            ("name", "Назва"),
            ("category", "Категорія"),
            ("quantity", "Кількість"),
            ("price", "Ціна"),
            ("location", "Склад / полиця")
        ]

        for index, (key, label) in enumerate(labels):

            row, col = divmod(index, 3)

            ttk.Label(
                form,
                text=label
            ).grid(
                row=row * 2,
                column=col,
                sticky="w",
                padx=6
            )

            ttk.Entry(
                form,
                textvariable=self.vars[key],
                width=30
            ).grid(
                row=row * 2 + 1,
                column=col,
                sticky="ew",
                padx=6,
                pady=(2, 8)
            )

            form.columnconfigure(col, weight=1)

        # Кнопки
        buttons = ttk.Frame(
            self.root,
            padding=(12, 0, 12, 10)
        )

        buttons.pack(fill="x")

        ttk.Button(
            buttons,
            text="Додати",
            command=self.add_product
        ).pack(side="left", padx=4)

        ttk.Button(
            buttons,
            text="Оновити вибраний",
            command=self.update_product
        ).pack(side="left", padx=4)

        ttk.Button(
            buttons,
            text="Видалити вибраний",
            command=self.delete_product
        ).pack(side="left", padx=4)

        ttk.Button(
            buttons,
            text="Очистити форму",
            command=self.clear_form
        ).pack(side="left", padx=4)

        ttk.Button(
            buttons,
            text="Синхронізувати",
            command=self.synchronize
        ).pack(side="left", padx=4)

        ttk.Button(
            buttons,
            text="Експорт CSV",
            command=self.export_csv
        ).pack(side="left", padx=4)

        # Рядок стану
        self.status_var = tk.StringVar(value="Готово.")

        status = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief="sunken",
            anchor="w",
            padding=(8, 4)
        )

        status.pack(side="bottom", fill="x")

    # ---------- DATA ----------

    # Перетворення словника на об'єкт Product
    def convert_product(self, data):
        return Product(
            id=str(data["id"]),
            name=data["name"],
            category=data["category"],
            quantity=int(data["quantity"]),
            price=float(data["price"]),
            location=data["location"],
            created_at=data.get("created_at", "")
        )

    # Перетворення форми на словник для API
    def validate_form(self):

        name = self.vars["name"].get().strip()
        category = self.vars["category"].get().strip()

        quantity_text = self.vars["quantity"].get().strip()

        price_text = (
            self.vars["price"].get()
            .strip()
            .replace(",", ".")
        )

        location = self.vars["location"].get().strip()

        if not name or not category or not location:
            raise ValueError(
                "Заповніть назву, категорію та місце зберігання."
            )

        if not quantity_text:
            raise ValueError("Введіть кількість.")

        try:
            quantity = int(quantity_text)
        except ValueError:
            raise ValueError(
                "Кількість повинна бути цілим числом."
            )

        if quantity < 0:
            raise ValueError(
                "Кількість не може бути від'ємною."
            )

        if not price_text:
            raise ValueError("Введіть ціну.")

        try:
            price = float(price_text)
        except ValueError:
            raise ValueError(
                "Ціна повинна бути числом."
            )

        if price < 0:
            raise ValueError(
                "Ціна не може бути від'ємною."
            )

        return {
            "name": name,
            "category": category,
            "quantity": quantity,
            "price": price,
            "location": location
        }

    # Завантаження товарів із сервера або кешу
    def load_products(self):

        try:
            data = self.api.get_items()

            self.products = [
                self.convert_product(item)
                for item in data
            ]

            self.refresh_table()

            if self.api.online:
                self.set_status(
                    f"Підключено до сервера. Товарів: {len(self.products)}"
                )
            else:
                self.set_status(
                    f"Офлайн-режим. Завантажено з кешу: {len(self.products)}"
                )

        except (ValueError, KeyError, TypeError) as error:
            self.set_status(f"Помилка даних: {error}")
            messagebox.showerror("Помилка", str(error))

    # Пошук товару за ID
    def find_product(self, product_id):

        return next(
            p for p in self.products
            if str(p.id) == str(product_id)
        )

    # Оновлення списку після операції
    def reload_products(self):
        self.load_products()

    # ---------- CRUD ----------

    # Додавання товару
    def add_product(self):

        try:
            data = self.validate_form()

            self.api.create_item(data)

            self.reload_products()

            self.clear_form()

            self.set_status(
                f"Товар «{data['name']}» додано."
            )

        except (ValueError, KeyError, TypeError) as error:
            self.show_error(error)

        except Exception as error:
            self.show_error(error)

    # Редагування товару
    def update_product(self):

        if self.selected_id is None:
            messagebox.showwarning(
                "Увага",
                "Спочатку виберіть товар у таблиці."
            )
            return

        try:
            data = self.validate_form()

            self.api.update_item(
                self.selected_id,
                data
            )

            self.reload_products()

            self.set_status(
                f"Товар ID {self.selected_id} оновлено."
            )

        except Exception as error:
            self.show_error(error)

    # Видалення товару
    def delete_product(self):

        if self.selected_id is None:
            messagebox.showwarning(
                "Увага",
                "Спочатку виберіть товар у таблиці."
            )
            return

        product = self.find_product(self.selected_id)

        answer = messagebox.askyesno(
            "Підтвердження",
            f"Видалити товар «{product.name}»?"
        )

        if answer:

            try:
                self.api.delete_item(self.selected_id)

                self.reload_products()

                self.clear_form()

                self.set_status(
                    f"Товар ID {product.id} видалено."
                )

            except Exception as error:
                self.show_error(error)

    # ---------- FORM ----------

    # Очищення форми
    def clear_form(self):

        for variable in self.vars.values():
            variable.set("")

        self.selected_id = None

        for item in self.tree.selection():
            self.tree.selection_remove(item)

    # Вибір товару з таблиці
    def on_select(self, event=None):

        selected = self.tree.selection()

        if not selected:
            return

        product_id = selected[0]

        product = self.find_product(product_id)

        self.selected_id = product_id

        for key in self.vars:
            self.vars[key].set(
                str(getattr(product, key))
            )

        self.set_status(
            f"Вибрано товар ID {product_id}."
        )

    # ---------- TABLE ----------

    # Оновлення таблиці
    def refresh_table(self):

        query = self.search_var.get().strip().casefold()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for product in self.products:

            if (
                query
                and query not in product.name.casefold()
                and query not in product.category.casefold()
            ):
                continue

            self.tree.insert(
                "",
                "end",
                iid=str(product.id),
                values=(
                    product.id,
                    product.name,
                    product.category,
                    product.quantity,
                    f"{product.price:.2f}",
                    product.location
                )
            )

        self.set_status(
            f"Записів: {len(self.products)} | "
            f"Показано: {len(self.tree.get_children())}"
        )

    # Сортування таблиці
    def sort_by(self, column):

        items = [
            (self.tree.set(item, column), item)
            for item in self.tree.get_children()
        ]

        reverse = getattr(
            self,
            "_sort_reverse",
            {}
        ).get(column, False)

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

    # ---------- SYNCHRONIZATION ----------

    # Синхронізація з сервером
    def synchronize(self):

        try:
            data = self.api.synchronize()

            self.products = [
                self.convert_product(item)
                for item in data
            ]

            self.refresh_table()

            self.set_status(
                f"Синхронізацію завершено. Товарів: {len(self.products)}"
            )

            messagebox.showinfo(
                "Синхронізація",
                "Дані успішно синхронізовано із сервером."
            )

        except Exception as error:
            self.set_status(
                f"Помилка синхронізації: {error}"
            )

            messagebox.showerror(
                "Помилка синхронізації",
                str(error)
            )

    # Експорт CSV
    def export_csv(self):

        path = filedialog.asksaveasfilename(
            title="Експорт CSV",
            defaultextension=".csv",
            filetypes=[("CSV файли", "*.csv")]
        )

        if not path:
            return

        try:
            self.api.export_csv(path)

            self.set_status(
                "CSV успішно експортовано."
            )

            messagebox.showinfo(
                "Експорт",
                "Файл успішно збережено."
            )

        except Exception as error:
            self.show_error(error)

    # ---------- ERRORS ----------

    # Виведення повідомлення про помилку
    def show_error(self, error):

        self.set_status(f"Помилка: {error}")

        messagebox.showerror(
            "Помилка",
            str(error)
        )

    # Зміна тексту статус-бару
    def set_status(self, message):

        self.status_var.set(message)


# ---------- START PROGRAM ----------

if __name__ == "__main__":

    root = tk.Tk()

    app = InventoryApp(root)

    root.mainloop()
