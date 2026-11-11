
import csv
import json
import uuid
from pathlib import Path
from datetime import datetime

import requests


SERVER_URL = "http://127.0.0.1:5000"

CACHE_FILE = Path(__file__).parent / "cache.csv"
PENDING_FILE = Path(__file__).parent / "pending.json"

FIELDS = [
    "id", "name", "category", "quantity",
    "price", "location", "created_at"
]


class InventoryAPI:

    def __init__(self):
        self.online = False

    # ---------- CACHE ----------

    # Зберігаємо товари у локальний кеш
    def save_cache(self, items):
        with CACHE_FILE.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(items)

    # Завантажуємо товари з кешу
    def load_cache(self):
        if not CACHE_FILE.exists():
            return []

        with CACHE_FILE.open("r", newline="", encoding="utf-8") as file:
            items = list(csv.DictReader(file))

        for item in items:
            item["quantity"] = int(item["quantity"])
            item["price"] = float(item["price"])

        return items

    # Читаємо чергу офлайн-операцій
    def read_pending(self):
        if not PENDING_FILE.exists():
            return []

        return json.loads(
            PENDING_FILE.read_text(encoding="utf-8")
        )

    # Зберігаємо чергу офлайн-операцій
    def save_pending(self, operations):
        PENDING_FILE.write_text(
            json.dumps(operations, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    # ---------- GET ----------

    # Отримати всі товари
    def get_items(self):
        try:
            response = requests.get(
                f"{SERVER_URL}/items",
                timeout=3
            )

            response.raise_for_status()

            items = response.json()

            self.save_cache(items)

            self.online = True

            return items

        except (requests.ConnectionError, requests.Timeout):
            self.online = False

            return self.load_cache()

    # ---------- POST ----------

    # Додати товар
    def create_item(self, data):
        try:
            response = requests.post(
                f"{SERVER_URL}/items",
                json=data,
                timeout=3
            )

            response.raise_for_status()

            self.online = True

            self.get_items()

            return response.json()

        except (requests.ConnectionError, requests.Timeout):
            self.online = False

            items = self.load_cache()

            local_id = "local-" + str(uuid.uuid4())

            item = {
                "id": local_id,
                **data,
                "created_at": datetime.now().isoformat()
            }

            items.append(item)

            self.save_cache(items)

            operations = self.read_pending()

            operations.append({
                "action": "create",
                "id": local_id,
                "data": data
            })

            self.save_pending(operations)

            return item

    # ---------- PUT ----------

    # Редагувати товар
    def update_item(self, item_id, data):
        try:
            response = requests.put(
                f"{SERVER_URL}/items/{item_id}",
                json=data,
                timeout=3
            )

            response.raise_for_status()

            self.online = True

            self.get_items()

            return response.json()

        except (requests.ConnectionError, requests.Timeout):
            self.online = False

            items = self.load_cache()

            found = False

            for item in items:
                if item["id"] == item_id:
                    item.update(data)
                    found = True
                    break

            if not found:
                raise ValueError("Товар не знайдено в кеші.")

            self.save_cache(items)

            operations = self.read_pending()

            # Якщо товар створений офлайн
            create_operation = next(
                (
                    op for op in operations
                    if op["id"] == item_id
                    and op["action"] == "create"
                ),
                None
            )

            if create_operation:
                create_operation["data"] = data

            else:
                operations = [
                    op for op in operations
                    if not (
                        op["id"] == item_id
                        and op["action"] == "update"
                    )
                ]

                operations.append({
                    "action": "update",
                    "id": item_id,
                    "data": data
                })

            self.save_pending(operations)

            return next(
                item for item in items
                if item["id"] == item_id
            )

    # ---------- DELETE ----------

    # Видалити товар
    def delete_item(self, item_id):
        try:
            response = requests.delete(
                f"{SERVER_URL}/items/{item_id}",
                timeout=3
            )

            response.raise_for_status()

            self.online = True

            self.get_items()

            return response.json()

        except (requests.ConnectionError, requests.Timeout):
            self.online = False

            items = self.load_cache()

            new_items = [
                item for item in items
                if item["id"] != item_id
            ]

            if len(new_items) == len(items):
                raise ValueError("Товар не знайдено в кеші.")

            self.save_cache(new_items)

            operations = self.read_pending()

            # Якщо товар був створений офлайн
            if any(
                op["id"] == item_id
                and op["action"] == "create"
                for op in operations
            ):
                operations = [
                    op for op in operations
                    if op["id"] != item_id
                ]

            else:
                operations = [
                    op for op in operations
                    if not (
                        op["id"] == item_id
                        and op["action"] in ("update", "delete")
                    )
                ]

                operations.append({
                    "action": "delete",
                    "id": item_id
                })

            self.save_pending(operations)

            return {"message": "Товар видалено локально."}

    # ---------- SYNCHRONIZE ----------

    # Синхронізація із сервером
    def synchronize(self):
        operations = self.read_pending()

        id_map = {}

        # Відправляємо всі офлайн-операції
        for operation in operations:

            action = operation["action"]
            item_id = operation["id"]

            # Створення товару
            if action == "create":

                response = requests.post(
                    f"{SERVER_URL}/items",
                    json=operation["data"],
                    timeout=5
                )

                response.raise_for_status()

                id_map[item_id] = response.json()["id"]

            # Оновлення товару
            elif action == "update":

                real_id = id_map.get(item_id, item_id)

                response = requests.put(
                    f"{SERVER_URL}/items/{real_id}",
                    json=operation["data"],
                    timeout=5
                )

                response.raise_for_status()

            # Видалення товару
            elif action == "delete":

                real_id = id_map.get(item_id, item_id)

                response = requests.delete(
                    f"{SERVER_URL}/items/{real_id}",
                    timeout=5
                )

                if response.status_code != 404:
                    response.raise_for_status()

        # Очищуємо чергу після успішної синхронізації
        self.save_pending([])

        # Завантажуємо актуальні дані
        response = requests.get(
            f"{SERVER_URL}/items",
            timeout=5
        )

        response.raise_for_status()

        items = response.json()

        self.save_cache(items)

        self.online = True

        return items

    # ---------- EXPORT ----------

    # Експорт CSV із сервера
    def export_csv(self, destination):
        response = requests.get(
            f"{SERVER_URL}/export",
            timeout=5
        )

        response.raise_for_status()

        Path(destination).write_bytes(response.content)
