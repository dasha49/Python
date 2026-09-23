from models import Medicine, Antibiotic, Vitamin, Vaccine


def print_medicines(medicines: list[Medicine]) -> None:
    for medicine in medicines:
        print(medicine.info())


medicines = [
    Antibiotic("Амоксицилін", 10, 50.0),
    Vitamin("Вітамін C", 20, 25.0),
    Vaccine("Вакцина X", 5, 100.0),
]

print_medicines(medicines)
