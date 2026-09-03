def calculate_expression(expression: str):
    # 1. Лексичний аналіз (Токенізатор)
    # Перетворює рядок "2 + 3 * 4" на список [2.0, '+', 3.0, '*', 4.0]
    def tokenize(expr):
        tokens = []
        i = 0
        while i < len(expr):
            char = expr[i]
            if char.isspace():
                i += 1
                continue
            if char in "+-*/()":
                tokens.append(char)
                i += 1
            elif char.isdigit() or char == '.':
                num_str = ""
                while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
                    num_str += expr[i]
                    i += 1
                try:
                    tokens.append(float(num_str))
                except ValueError:
                    raise ValueError(f"Невірний формат числа: {num_str}")
            else:
                raise ValueError(f"Невідомий символ: {char}")
        return tokens

    # 2. Синтаксичний аналізатор (Рекурсивний спуск)
    class Parser:
        def __init__(self, tokens):
            self.tokens = tokens
            self.pos = 0

        def current(self):
            if self.pos < len(self.tokens):
                return self.tokens[self.pos]
            return None

        def consume(self):
            self.pos += 1

        # Обробка чисел, дужок та унарних плюсів/мінусів (найвищий пріоритет)
        def parse_factor(self):
            token = self.current()
            if token == '+':
                self.consume()
                return self.parse_factor()
            elif token == '-':
                self.consume()
                return -self.parse_factor()
            elif isinstance(token, float):
                self.consume()
                return token
            elif token == '(':
                self.consume()
                result = self.parse_expression()
                if self.current() != ')':
                    raise ValueError("Пропущена закриваюча дужка ')'")
                self.consume()
                return result
            else:
                raise ValueError(f"Неочікуваний символ: {token}")

        # Обробка множення та ділення (середній пріоритет)
        def parse_term(self):
            result = self.parse_factor()
            while self.current() in ('*', '/'):
                op = self.current()
                self.consume()
                right = self.parse_factor()
                if op == '*':
                    result *= right
                elif op == '/':
                    if right == 0:
                        raise ZeroDivisionError("Ділення на нуль неможливе")
                    result /= right
            return result

        # Обробка додавання та віднімання (найнижчий пріоритет)
        def parse_expression(self):
            result = self.parse_term()
            while self.current() in ('+', '-'):
                op = self.current()
                self.consume()
                right = self.parse_term()
                if op == '+':
                    result += right
                elif op == '-':
                    result -= right
            return result

    # 3. Виконання
    try:
        if not expression.strip():
            return "Вираз порожній"
            
        tokens = tokenize(expression)
        parser = Parser(tokens)
        result = parser.parse_expression()
        
        # Перевірка, чи не залишилось зайвих токенів після парсингу
        if parser.current() is not None:
            raise ValueError(f"Зайвий символ у виразі: {parser.current()}")
            
        # Повертаємо ціле число, якщо дробова частина дорівнює нулю (напр. 14.0 -> 14)
        return int(result) if result.is_integer() else result
        
    except Exception as e:
        return f"Помилка: {e}"

# Інтерактивна частина для перевірки
if __name__ == "__main__":
    print("Просунутий калькулятор (для виходу введіть 'exit' або 'q')")
    while True:
        user_input = input("Введіть математичний вираз: ")
        if user_input.lower() in ('exit', 'q'):
            break
        
        output = calculate_expression(user_input)
        print(f"Результат: {output}\n")