import psycopg2
import os
import csv
from configparser import ConfigParser
from datetime import datetime
import glob
from pgdb import PGDatabase
from 

def load_config(config_file='config.ini'):
    config = ConfigParser()
    config.read(config_file, encoding='utf-8')
    return config

def parse_filename(filename):
    basename = os.path.basename(filename)
    name_without_ext = basename.replace('.csv', '')
    parts = name_without_ext.split('_')
    
    if len(parts) >= 3:
        sale_date = parts[0]
        shop_num = int(parts[1])
        cash_num = int(parts[2])
        return sale_date, shop_num, cash_num
    else:
        raise ValueError(f"Некорректный формат имени файла: {basename}")

def load_all_files():
    config = load_config()
    
    sales_path = config.get('Files', 'SALES_PATH')
    
    db_params = {
        'host': config.get('Database', 'HOST').strip(),
        'database': config.get('Database', 'DATABASE'),
        'user': config.get('Database', 'USER'),
        'password': config.get('Database', 'PASSWORD')
    }
    
    pattern = os.path.join(sales_path, '*.csv')
    csv_files = glob.glob(pattern)
    
    if not csv_files:
        print(f"CSV файлы не найдены в {sales_path}")
        return
    
    print(f"Найдено файлов: {len(csv_files)}")
    
    try:
        db = PGDatabase(
            host=db_params['host'],
            database=db_params['database'],
            user=db_params['user'],
            password=db_params['password']
        )
        
        
        create_result = db.post("""
            CREATE TABLE IF NOT EXISTS sales (
                id SERIAL PRIMARY KEY,
                doc_id VARCHAR(10) NOT NULL,
                shop_num INTEGER NOT NULL,
                cash_num INTEGER NOT NULL,
                sale_date DATE NOT NULL,
                item VARCHAR(200) NOT NULL,
                category VARCHAR(100) NOT NULL,
                amount INTEGER NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                discount DECIMAL(10, 2) DEFAULT 0
            )
        """)
        
        if create_result:
            print("Таблица создана/уже существует")
        else:
            print("Ошибка при создании таблицы")
            return
        
        total_records = 0
        successful_files = []
        failed_files = []
        
        for filepath in csv_files:
            try:
                sale_date_str, shop_num, cash_num = parse_filename(filepath)
                sale_date = datetime.strptime(sale_date_str, '%Y-%m-%d').date()
                                
                with open(filepath, 'r', encoding='utf-8-sig') as csvfile:
                    reader = csv.DictReader(csvfile)
                    count = 0
                    
                    for row in reader:
                        insert_sql = """
                        INSERT INTO sales 
                        (doc_id, shop_num, cash_num, sale_date, item, category, amount, price, discount)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        args = (
                            row['doc_id'],
                            shop_num,
                            cash_num,
                            sale_date,
                            row['item'],
                            row['category'],
                            int(row['amount']),
                            float(row['price']),
                            float(row['discount'])
                        )
                        
                        if db.post(insert_sql, args):
                            count += 1
                            total_records += 1
                    
                                       
                    # Если файл успешно загружен, добавляем в список на удаление
                    if count > 0:
                        successful_files.append(filepath)
                
            except Exception as e:
                print(f"  Ошибка: {e}")
                failed_files.append(filepath)
        
        # Удаляем успешно загруженные файлы
        if successful_files:
            
            for filepath in successful_files:
                try:
                    os.remove(filepath)
                    
                except Exception as e:
                    print(f"  Ошибка при удалении {os.path.basename(filepath)}: {e}")
        
        # Выводим информацию о неудачных файлах
        if failed_files:
            print(f"\nНе удалось загрузить {len(failed_files)} файлов:")
            for filepath in failed_files:
                print(f"  {os.path.basename(filepath)}")
        
        print(f"\nВсего загружено записей: {total_records}")
        print(f"Удалено файлов: {len(successful_files)}")
        print(f"Осталось файлов: {len(failed_files)}")
        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    load_all_files()