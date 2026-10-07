from abc import ABC, abstractmethod


class JunkItem:
    def __init__(self, name: str, quantity: int, value: float):
        self.name = name
        self.quantity = quantity
        self.value = value

    def __str__(self):
        return f"{self.name}: кількість = {self.quantity}, ціна = {self.value}"


class StorageBackend(ABC):
    @abstractmethod
    def save(self, items: list[JunkItem]):
        pass

    @abstractmethod
    def load(self) -> list[JunkItem]:
        pass


class FileJunkStorage(StorageBackend):
    def __init__(self, filename: str):
        self.filename = filename

    def save(self, items: list[JunkItem]):
        with open(self.filename, "w", encoding="utf-8") as file:
            for item in items:
                value = str(item.value).replace(".", ",")

                file.write(
                    f"{item.name}|{item.quantity}|{value}\n"
                )

    def load(self) -> list[JunkItem]:
        items = []

        with open(self.filename, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                if not line:
                    continue

                parts = line.split("|")

                if len(parts) != 3:
                    print(
                        f"Попередження: рядок {line_number} пропущено "
                        f"(потрібно 3 поля)."
                    )
                    continue

                name = parts[0].strip()
                quantity_text = parts[1].strip()
                value_text = parts[2].strip()

                try:
                    quantity = int(quantity_text)
                    value = float(value_text.replace(",", "."))
                except ValueError:
                    print(
                        f"Попередження: рядок {line_number} пропущено "
                        f"(кількість має бути int, ціна — float)."
                    )
                    continue

                items.append(JunkItem(name, quantity, value))

        return items


class JunkStorage:
    def __init__(self, backend: StorageBackend):
        self.backend = backend

    def add(self, item: JunkItem):
        items = self.backend.load()
        items.append(item)
        self.backend.save(items)

    def get_all(self) -> list[JunkItem]:
        return self.backend.load()

    def clear(self):
        self.backend.save([])


# Демонстрація роботи

storage = JunkStorage(
    FileJunkStorage("junk.csv")
)

items = [
    JunkItem("Бляшанка", 5, 2.5),
    JunkItem("Стара плата", 3, 7.8),
    JunkItem("Купка дротів", 10, 1.2)
]

# Записуємо предмети у файл
storage.backend.save(items)

print("Предмети записані у файл.\n")

# Читаємо предмети назад
loaded_items = storage.get_all()

print("Предмети після читання з файлу:")

for item in loaded_items:
    print(item)
