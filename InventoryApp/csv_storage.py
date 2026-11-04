import csv
from pathlib import Path
from product import Product


FIELDS = ["id", "name", "category", "quantity", "price", "location", "created_at"]


class CSVStorage:
    """Клас для читання та запису товарів у CSV."""

    def load(self, file_path):
        path = Path(file_path)
        if not path.exists():
            return []

        products = []
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    products.append(Product(
                        id=int(row["id"]),
                        name=row["name"],
                        category=row["category"],
                        quantity=int(row["quantity"]),
                        price=float(row["price"]),
                        location=row.get("location", ""),
                        created_at=row.get("created_at", ""),
                    ))
                except (ValueError, KeyError, TypeError) as error:
                    raise ValueError(f"Некоректний рядок CSV: {row}. Деталі: {error}") from error
        return products

    def save(self, file_path, products):
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()
            for product in products:
                writer.writerow(product.to_dict())
