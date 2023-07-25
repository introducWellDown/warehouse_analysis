import pandas as pd
import json
from pandas import json_normalize

file_path = "trial_task.json"

with open(file_path, 'r', encoding='utf-8') as json_file:
    json_data = json_file.read()

data = json.loads(json_data)

df = pd.DataFrame(data)

# Задача 1: Найти тариф стоимости доставки для каждого склада
# Группируем по складам и вычисляем сумму стоимости доставки

tariffs = df.groupby('warehouse_name')['highway_cost'].sum().reset_index()

print("Резултат задачи №1")
print("Тарифы доставки для каждого склада:")
print(tariffs)

# Задача 2: Найти суммарное количество, суммарный доход,
# суммарный расход и суммарную прибыль для каждого товара

# Нормализуем столбец 'products' и также включим столбец 'order_id' в список meta
df_products = json_normalize(data, 'products', ['order_id', 'warehouse_name', 'highway_cost'])

# Вычисляем доход, расход и прибыль для каждого товара
df_products['income'] = df_products['price'] * df_products['quantity']
df_products['expenses'] = df_products['highway_cost'] * df_products['quantity']
df_products['profit'] = df_products['income'] - df_products['expenses']

# Группируем данные по продуктам и вычисляем суммарные значения
result_df = df_products.groupby(['order_id', 'product', 'warehouse_name'])[['quantity', 'income', 'expenses', 'profit']].sum().reset_index()

print("Резултат задачи №2")
print("Суммарные значения по продуктам:")
print(result_df)


# Задача 3: Составить табличку со столбцами 'order_id' (id заказа) и 'order_profit' (прибыль полученная с заказа)

# Группируем данные по заказам и вычисляем суммарную прибыль для каждого заказа
order_profit_df = result_df.groupby('order_id')['profit'].sum().reset_index()
order_profit_df.rename(columns={'profit': 'order_profit'}, inplace=True)

print("Резултат задачи №3")
print("Табличка с прибылью по каждому заказу:")
print(order_profit_df)

# Вывод средней прибыли заказаов 
average_order_profit = order_profit_df['order_profit'].mean()
print(f"Средняя прибыль заказов: {average_order_profit}")

# Задача 4: Составить табличку типа 'warehouse_name', 'product', 'quantity', 'profit', 'percent_profit_product_of_warehouse'

# Вычисляем общую прибыль для каждого склада
warehouse_total_profit = result_df.groupby('warehouse_name')['profit'].sum()

# Объединяем с result_df, чтобы получить общую прибыль для каждой строки
result_df = result_df.merge(warehouse_total_profit, on='warehouse_name', suffixes=('', '_total'))

# Вычисляем процентную прибыль каждого товара относительно склада
result_df['percent_profit_product_of_warehouse'] = (result_df['profit'] / result_df['profit_total']) * 100

# Выбираем нужные столбцы
final_table = result_df[['warehouse_name', 'product', 'quantity', 'profit', 'percent_profit_product_of_warehouse' ]]

print("Резултат задачи №4")
print("Таблица с результатами:")
print(final_table)

# Задача 5: Отсортировать 'percent_profit_product_of_warehouse' по убыванию и вычислить накопленный процент

# Сортируем DataFrame по столбцу 'percent_profit_product_of_warehouse' по убыванию
final_table = final_table.sort_values(by='percent_profit_product_of_warehouse', ascending=False)

# Вычисляем накопленный процент
final_table['accumulated_percent_profit_product_of_warehouse'] = final_table['percent_profit_product_of_warehouse'] \
    .cumsum().map('{:.2f}%'.format)

print("Резултат задачи №5")
print("Таблица с результатами:")
print(final_table)

# Задача 6: Присвоить категории 'A', 'B' или 'C' на основании накопленного процента

# Функция для определения категории
def assign_category(accumulated_percent):
    if accumulated_percent <= 70:
        return 'A'
    elif 70 < accumulated_percent <= 90:
        return 'B'
    else:
        return 'C'

# Применяем функцию к столбцу 'accumulated_percent_profit_product_of_warehouse' для получения категорий
final_table['category'] = final_table['accumulated_percent_profit_product_of_warehouse'] \
    .str.rstrip('%').astype(float).apply(assign_category)

print("Резултат задачи №6")
print("Таблица с результатами:")
print(final_table)