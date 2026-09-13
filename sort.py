def check_clients(deals):
    result = []

    for deal in deals:
        name = deal["name"]
        amount = deal["amount"]
        status = deal["status"]

        # Перевіряємо, чи сума є числом
        if not isinstance(amount, (int, float)):
            category = "Фальшиві дані"
        # Визначаємо категорію за сумою
        elif amount < 100:
            category = "Дрібнота"
        elif amount < 1000:
            category = "Середнячо"
        else:
            category = "Великий клієнт"

        # Визначаємо рішення за статусом
        match status:
            case "clean":
                decision = "Працювати без питань"
            case "suspicious":
                decision = "Перевірити документи"
            case "fraud":
                decision = "У чорний список"
            case _:
                decision = "Невідомий статус"

        result.append({
            "name": name,
            "category": category,
            "decision": decision
        })

    return result


deals = [
    {"name": "Анна", "amount": 50, "status": "clean"},
    {"name": "Катя", "amount": 500, "status": "suspicious"},
    {"name": "Марія", "amount": 1500, "status": "clean"},
    {"name": "Женя", "amount": "1000", "status": "fraud"},
    {"name": "Софія", "amount": 300, "status": "unknown"}
]

clients = check_clients(deals)

print(clients)
