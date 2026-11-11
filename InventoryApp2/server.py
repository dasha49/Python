
from flask import Flask, request, jsonify, Response
from pathlib import Path
import csv
import uuid
from datetime import datetime

app = Flask(__name__)

# Шлях до файлу з товарами
DATA_DIR = Path(__file__).parent / "data"
CSV_FILE = DATA_DIR / "inventory.csv"

FIELDS = [
    "id", "name", "category", "quantity",
    "price", "location", "created_at"
]


# Створюємо CSV, якщо його ще немає
def ensure_file():
    DATA_DIR.mkdir(exist_ok=True)

    if not CSV_FILE.exists():
        with CSV_FILE.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()


# Читаємо всі товари з CSV
def read_items():
    ensure_file()

    with CSV_FILE.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


# Записуємо товари у CSV
def write_items(items):
    ensure_file()

    with CSV_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(items)


# Перевірка правильності даних
def validate_item(data):
    if not isinstance(data, dict):
        return "Дані повинні бути JSON-об'єктом."

    required = [
        "name", "category", "quantity",
        "price", "location"
    ]

    for field in required:
        if field not in data:
            return f"Відсутнє поле: {field}"

    for field in ["name", "category", "location"]:
        if not isinstance(data[field], str) or not data[field].strip():
            return f"Поле {field} повинно бути непорожнім рядком."

    if (
        isinstance(data["quantity"], bool)
        or not isinstance(data["quantity"], int)
        or data["quantity"] < 0
    ):
        return "Кількість повинна бути цілим числом >= 0."

    try:
        price = float(data["price"])

        if price < 0:
            return "Ціна повинна бути >= 0."

    except (TypeError, ValueError):
        return "Ціна повинна бути числом."

    return None


# Перетворюємо CSV-дані на правильні типи
def normalize_item(item):
    return {
        "id": item["id"],
        "name": item["name"],
        "category": item["category"],
        "quantity": int(item["quantity"]),
        "price": float(item["price"]),
        "location": item["location"],
        "created_at": item["created_at"]
    }


# GET: отримати всі товари
@app.route("/items", methods=["GET"])
def get_items():
    try:
        items = read_items()
        return jsonify([normalize_item(item) for item in items])

    except (ValueError, KeyError):
        return jsonify({"error": "Помилка читання CSV."}), 500


# POST: створити новий товар
@app.route("/items", methods=["POST"])
def create_item():
    data = request.get_json(silent=True)

    error = validate_item(data)

    if error:
        return jsonify({"error": error}), 400

    items = read_items()

    item = {
        "id": str(uuid.uuid4()),
        "name": data["name"].strip(),
        "category": data["category"].strip(),
        "quantity": str(data["quantity"]),
        "price": str(float(data["price"])),
        "location": data["location"].strip(),
        "created_at": datetime.now().isoformat(timespec="seconds")
    }

    items.append(item)
    write_items(items)

    return jsonify(normalize_item(item)), 201


# PUT: оновити товар
@app.route("/items/<item_id>", methods=["PUT"])
def update_item(item_id):
    data = request.get_json(silent=True)

    error = validate_item(data)

    if error:
        return jsonify({"error": error}), 400

    items = read_items()

    for item in items:
        if item["id"] == item_id:
            item["name"] = data["name"].strip()
            item["category"] = data["category"].strip()
            item["quantity"] = str(data["quantity"])
            item["price"] = str(float(data["price"]))
            item["location"] = data["location"].strip()

            write_items(items)

            return jsonify(normalize_item(item))

    return jsonify({"error": "Товар не знайдено."}), 404


# DELETE: видалити товар
@app.route("/items/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    items = read_items()

    new_items = [
        item for item in items
        if item["id"] != item_id
    ]

    if len(new_items) == len(items):
        return jsonify({"error": "Товар не знайдено."}), 404

    write_items(new_items)

    return jsonify({"message": "Товар видалено."})


# EXPORT: отримати CSV із сервера
@app.route("/export", methods=["GET"])
def export_csv():
    ensure_file()

    content = CSV_FILE.read_text(encoding="utf-8")

    return Response(
        content,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=inventory.csv"
        }
    )


# Запуск сервера
if __name__ == "__main__":
    ensure_file()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
