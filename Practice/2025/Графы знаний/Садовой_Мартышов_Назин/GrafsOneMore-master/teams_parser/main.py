import csv
import os
import random
import string

def generate_short_id(existing_ids, length=6):
    """Генерирует короткий уникальный идентификатор"""
    while True:
        new_id = ''.join(random.choices(string.ascii_letters, k=length))
        if new_id not in existing_ids:
            return new_id

def is_valid_row(row):
    """Проверяет, что строка не содержит пустых или N/A значений"""
    invalid_values = ['', 'null', 'n/a', 'none', 'nan']
    return all(cell.strip().lower() not in invalid_values for cell in row)

def process_teams(input_path, output_path):
    """Основная функция обработки CSV"""
    existing_ids = set()
    
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        
        headers = next(reader)
        
        writer.writerow(['Team ID'] + headers)
        
        
        for row in reader:
            if not row:  
                continue
                
            if is_valid_row(row):
                team_id = generate_short_id(existing_ids)
                existing_ids.add(team_id)
                writer.writerow([team_id] + row)

def run(unknown_args):
    input_file = './parsed_csv/teams.csv'
    output_file = './parsed_csv/teams_processed.csv'
    
    
    if not os.path.exists(input_file):
        print(f"Ошибка: Входной файл {input_file} не найден")
        return
    
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    try:
        process_teams(input_file, output_file)
        print(f"Успешно обработано! Результат сохранен в {output_file}")
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")

if __name__ == "__main__":
    run([])