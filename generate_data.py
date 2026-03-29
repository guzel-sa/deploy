import os
import random
import csv
from datetime import datetime

# Создаем папку data, если её нет
os.makedirs('data', exist_ok=True)

# Категории и товары с базовыми ценами
PRODUCTS = {
    'стиральные порошки': {
        'порошок для детского белья 400гр': 500,
        'жидкий порошок 1л': 780,
        'порошок для цветного 200гр': 467,
        'порошок для деликатных тканей 800гр': 750
    },
    'мыло': {
        'детское мыло 100г': 60,
        'банное мыло 150гр': 120,
        'хозяйственное мыло 200гр': 120,
        'ароматное мыло 100гр': 240,
        'жидкое мыло 500мл': 340
    }
}

def generate_doc_id():
    """Генерирует численно-буквенный идентификатор чека"""
    letters = random.choices('ABCDEFGHJKLMNPQRSTUVWXYZ', k=2)
    numbers = random.randint(10000, 99999)
    return f"{''.join(letters)}{numbers}"

def generate_price(base_price):
    """Генерирует цену с колебанием ±20%"""
    variation = random.uniform(0.8, 1.2)
    return round(base_price * variation, 2)

def generate_discount():
    """Генерирует скидку: чаще 0, иногда до 30%"""
    if random.random() < 0.3: 
        return round(random.uniform(0.01, 0.3) * 100, 2)  
    return 0

def generate_receipt_items(num_items):
    """Генерирует список товаров для одного чека"""
    items = []
    all_products = []
    
    # Создаем список всех доступных товаров
    for category, products in PRODUCTS.items():
        for product_name, base_price in products.items():
            all_products.append((category, product_name, base_price))
    
    for _ in range(num_items):
        category, product_name, base_price = random.choice(all_products)
        price = generate_price(base_price)
        amount = random.randint(1, 5)
        discount_percent = generate_discount()
        
        
        items.append({
            'doc_id': None,  # будет заполнен позже для всех позиций чека
            'item': product_name,
            'category': category,
            'amount': amount,
            'price': price,
            'discount': discount_percent
        })
    
    return items

def generate_file(shop_num, cash_num, current_date):
    """Генерирует один файл выгрузки"""
    num_lines = random.randint(10, 50)
    filename = os.path.join('data', f"{current_date}_{shop_num}_{cash_num}.csv")
    remaining_lines = num_lines
    all_rows = []
    
    while remaining_lines > 0:
        # Количество позиций в чеке (1-4 позиций)
        items_in_receipt = random.randint(1, min(4, remaining_lines))
        remaining_lines -= items_in_receipt
        
        # Генерируем doc_id для чека
        doc_id = generate_doc_id()
        
        # Генерируем позиции чека
        items = generate_receipt_items(items_in_receipt)
        
        # Добавляем doc_id к каждой позиции
        for item in items:
            item['doc_id'] = doc_id
            all_rows.append(item)
    
    # Записываем в CSV файл
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['doc_id', 'item', 'category', 'amount', 'price', 'discount']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(all_rows)
        

def main():
    # Параметры генерации
    num_shops = 20  # магазины 1-20
    max_cash_per_shop = 3  # максимум касс в магазине
    
    # Получаем текущую дату
    current_date = datetime.now()
    date_str = current_date.strftime('%Y-%m-%d')
        
    # Проверяем, не воскресенье ли сегодня
    if current_date.weekday() != 1:  
            
        total_files = 0
    
        # Генерируем файлы для всех магазинов и касс
        for shop_num in range(1, num_shops + 1):
            # У каждого магазина разное количество касс (1-3)
            num_cash_registers = random.randint(1, max_cash_per_shop)
            
            for cash_num in range(1, num_cash_registers + 1):
                generate_file(shop_num, cash_num, date_str)
                total_files += 1
        
        print(f"В папке 'data' создано файлов: {total_files}'")
    

if __name__ == "__main__":
    main()