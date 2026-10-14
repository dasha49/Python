
def parse_transaction(line):
    """Перевіряє формат рядка та повертає суму або None."""
    parts = line.split()

    if len(parts) != 2:
        return None

    operation, amount_text = parts

    if not operation.isalpha():
        return None

    try:
        amount = float(amount_text)
    except ValueError:
        return None

    return amount


def shadow(limit=200):
    def decorator(func):
        def wrapper(*args, **kwargs):
            total = 0
            warning_shown = False
            iterator = iter(func(*args, **kwargs))

            while True:
                try:
                    line = next(iterator)
                except StopIteration as stop:
                    # Зберігаємо значення return генератора.
                    return stop.value

                amount = parse_transaction(line)

                if amount is not None:
                    total += amount

                    if total > limit and not warning_shown:
                        print("Тіньовий ліміт перевищено. Активую схему")
                        warning_shown = True

                print(line)
                yield line

        return wrapper
    return decorator


def suspicious_counter(threshold=250):
    def decorator(func):
        def wrapper(*args, **kwargs):
            suspicious_total = 0
            iterator = iter(func(*args, **kwargs))

            while True:
                try:
                    line = next(iterator)
                except StopIteration as stop:
                    return stop.value

                amount = parse_transaction(line)

                # Незалежна перевірка суми однієї транзакції.
                if amount is not None and amount > threshold:
                    suspicious_total += amount
                    print(
                        f"Підозріла транзакція! "
                        f"Накопичена підозріла сума: {suspicious_total:g}"
                    )

                yield line

        return wrapper
    return decorator


@suspicious_counter(threshold=250)
@shadow(limit=200)
def generate_transactions():
    transactions = [
        "payment 120",
        "refund 50",
        "transfer 300",
        "payment 80",
        "refund abc",       # Некоректна сума
        "transfer 40 extra" # Неправильний формат
    ]

    total = 0

    for line in transactions:
        amount = parse_transaction(line)

        if amount is not None:
            total += amount

        yield line

    return total


# Отримуємо фінальне значення return генератора.
generator = generate_transactions()

while True:
    try:
        next(generator)
    except StopIteration as stop:
        print(f"Фінальна сума транзакцій: {stop.value:g}")
        break
