def calculate(a: float, b: float, operation: str):
    if operation == '+':
        return a + b
    elif operation == '-':
        return a - b
    elif operation == '*':
        return a * b
    elif operation == '/':
        if b == 0:
            return "Помилка: ділення на нуль неможливе"
        return a / b
    else:
        return "Помилка: непідтримувана операція"

try:
    num1 = float(input("Введіть перше число: "))
    op = input("Введіть операцію (+, -, *, /): ").strip()
    num2 = float(input("Введіть друге число: "))

    result = calculate(num1, num2, op)
    print(f"Результат: {result}")
except ValueError:
    print("Помилка: необхідно ввести числове значення")