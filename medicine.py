def check_medicines(medicines):
    result = []

    for medicine in medicines:
        name = medicine["name"]
        quantity = medicine["quantity"]
        temperature = medicine["temperature"]
        category = medicine["category"]

        # Перевіряємо типи даних
        if not isinstance(quantity, int) or not isinstance(temperature, float):
            temperature_status = "Помилка даних"
        else:
           
            if temperature < 5:
                temperature_status = "Надто холодно"
            elif temperature > 25:
                temperature_status = "Надто жарко"
            else:
                temperature_status = "Норма"

        # Визначаємо статус категорії через match case
        match category:
            case "antibiotic":
                category_status = "Рецептурний препарат"
            case "vitamin":
                category_status = "Вільний продаж"
            case "vaccine":
                category_status = "Потребує спецзберігання"
            case _:
                category_status = "Невідома категорія"

        result.append({
            "name": name,
            "category_status": category_status,
            "temperature_status": temperature_status
        })

    return result


medicines = [
    {
        "name": "Спазмалгон",
        "quantity": 50,
        "category": "tablet",
        "temperature": 20.0
    },
    {
        "name": "Вітамін C",
        "quantity": 100,
        "category": "vitamin",
        "temperature": 27.0
    },
    {
        "name": "Вакцина",
        "quantity": 20,
        "category": "vaccine",
        "temperature": 3.0
    },
    {
        "name": "Препарат X",
        "quantity": "50",
        "category": "unknown",
        "temperature": 10.0
    }
]

result = check_medicines(medicines)

print(result)
