import csv

class CSVWriter:
    @staticmethod
    def write(data, filename, headers):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)