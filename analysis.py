import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
    # 8. Додаємо можливість передавати CSV як аргумент через argparse
    parser = argparse.ArgumentParser(description="Аналіз даних про постачання ліків.")
    parser.add_argument("csv_file", nargs="?", default="supplies.csv", help="Шлях до файлу CSV (за замовчуванням: supplies.csv)")
    args = parser.parse_args()

    # 1. Завантажуємо дані з CSV за допомогою pandas
    df = pd.read_csv(args.csv_file)

    # 2. Обчислення за допомогою NumPy
    prices = df['price_per_unit'].to_numpy()
    quantities = df['quantity'].to_numpy()

    mean_price = np.mean(prices)
    median_quantity = np.median(quantities)
    std_price = np.std(prices)  # Для вибіркового можна використати np.std(prices, ddof=1)

    print("--- 2. Статистика (NumPy) ---")
    print(f"Середня ціна: {mean_price:.2f}")
    print(f"Медіана кількості: {median_quantity:.2f}")
    print(f"Стандартне відхилення ціни: {std_price:.2f}\n")

    # 4. Додаємо обчислене поле total_price у DataFrame
    df['total_price'] = df['quantity'] * df['price_per_unit']

    # 3. Знаходимо постачальника з найбільшим загальним прибутком / вартістю
    supplier_revenue = df.groupby('supplier')['total_price'].sum()
    top_supplier = supplier_revenue.idxmax()
    max_revenue = supplier_revenue.max()

    # 3. Обчислюємо сумарну кількість препаратів за категоріями
    category_totals = df.groupby('category')['quantity'].sum()

    print("--- 3. Сумарна кількість за категоріями ---")
    print(category_totals)
    print(f"\nПостачальник з найбільшим прибутком: {top_supplier} ({max_revenue:.2f})\n")

    # 3. Відфільтровуємо записи, де quantity < 100, і зберігаємо у low_supply.csv
    low_supply_df = df[df['quantity'] < 100]
    low_supply_filename = "low_supply.csv"
    low_supply_df.to_csv(low_supply_filename, index=False)
    print(f"Фільтровані дані збережено у {low_supply_filename}\n")

    # 5. Відсортуємо дані за total_price у порядку спадання й виведемо перші 3 рядки
    sorted_df = df.sort_values(by='total_price', ascending=False)
    print("--- 5. Топ-3 записи за total_price ---")
    print(sorted_df.head(3)[['supplier', 'category', 'quantity', 'price_per_unit', 'total_price']])
    print("\n")

    # 6. Створюємо простий звіт у форматі .txt
    report_filename = "report.txt"
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write("=== ЗВІТ ПРО ПОСТАЧАННЯ ===\n\n")
        f.write("1. Середні та статистичні показники:\n")
        f.write(f"   - Середня ціна препаратів: {mean_price:.2f}\n")
        f.write(f"   - Медіана кількості (quantity): {median_quantity:.2f}\n")
        f.write(f"   - Стандартне відхилення ціни: {std_price:.2f}\n\n")
        f.write("2. Найкращий постачальник:\n")
        f.write(f"   - Постачальник з найбільшим прибутком: {top_supplier} (Сума: {max_revenue:.2f})\n\n")
        f.write("3. Дефіцитні поставки:\n")
        f.write(f"   - Назва файлу з дефіцитними поставками (quantity < 100): {low_supply_filename}\n")

    print(f"Звіт згенеровано у файл {report_filename}\n")

    # 7. Побудова графіка (через matplotlib) розподілу кількості препаратів за категоріями
    plt.figure(figsize=(8, 5))
    plt.bar(category_totals.index, category_totals.values, color=['#4C72B0', '#55A868', '#C44E52'])
    plt.title("Розподіл загальної кількості препаратів за категоріями")
    plt.xlabel("Категорія")
    plt.ylabel("Загальна кількість (quantity)")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig("category_distribution.png") # Збереження графіка у файл
    plt.show()

if __name__ == "__main__":
    main()
