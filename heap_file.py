import struct
import os
import csv

class HeapFile:
    def __init__(self, heap_path: str, record_format: str, page_size: int):
        self.heap_path = heap_path
        self.record_format = record_format
        self.page_size = page_size
        self.record_size = struct.calcsize(record_format)
        self.records_per_page = self.page_size // self.record_size

    # Exporta un CSV a un heap file binario paginado.
    def export_to_heap(self, csv_path: str):
        with open(csv_path, 'r', encoding='utf-8') as csvfile, open(self.heap_path, 'wb') as heapfile:
            reader = csv.reader(csvfile)
            next(reader, None)
            
            current_page_records = []
            for row in reader:
                # Convertir datos según el formato
                formatted_row = self._format_row(row)
                current_page_records.append(formatted_row)
                
                if len(current_page_records) == self.records_per_page:
                    self._write_page_to_disk(heapfile, current_page_records)
                    current_page_records = []
            
            # Escribir registros restantes en la última página
            if current_page_records:
                self._write_page_to_disk(heapfile, current_page_records)

    # Lee una página del heap file y retorna sus registros.
    def read_page(self, page_id: int) -> list[tuple]:
        if not os.path.exists(self.heap_path):
            return []

        with open(self.heap_path, 'rb') as f:
            f.seek(page_id * self.page_size)
            page_data = f.read(self.page_size)
            
            if not page_data:
                return []
                
            records = []
            for i in range(self.records_per_page):
                offset = i * self.record_size
                record_bytes = page_data[offset : offset + self.record_size]
                
                # Ignora registros vacios
                if all(b == 0 for b in record_bytes):
                    continue
                    
                records.append(struct.unpack(self.record_format, record_bytes))
            return records
        
    # Escribe una lista de registros en la página indicada.
    def write_page(self, page_id: int, records: list[tuple]):
        with open(self.heap_path, 'r+b') as f:
            f.seek(page_id * self.page_size)
            self._write_page_to_disk(f, records)

    # Retorna el número total de páginas del heap file.
    def count_pages(self) -> int:
        if not os.path.exists(self.heap_path):
            return 0
        file_size = os.path.getsize(self.heap_path)
        return file_size // self.page_size

    # Private:

    # Convierte los campos del csv al formato binario esperado.
    def _format_row(self, row: list) -> tuple:
        formatted = []
        
        format_parts = self.record_format.split()
        for i, val in enumerate(row):
            fmt = format_parts[i]
            if 's' in fmt:
                size = int(fmt.replace('s', ''))
                formatted.append(val.encode('utf-8')[:size].ljust(size, b'\x00'))
            else:
                formatted.append(int(val))
        return tuple(formatted)

    # Empaqueta registros y rellena el resto de la página con ceros.
    def _write_page_to_disk(self, file_handle, records: list[tuple]):
        page_buffer = bytearray()
        for rec in records:
            page_buffer.extend(struct.pack(self.record_format, *rec))
        
        # Relleno para mantener el tamaño de página fijo
        padding_size = self.page_size - len(page_buffer)
        if padding_size > 0:
            page_buffer.extend(b'\x00' * padding_size)
        
        file_handle.write(page_buffer)

# id (int),birth_date (char[10]),first_name(char[30]),last_name(char[30]),gender(char[1]),hire_date(char[10])
PAGE_SIZE = 4096
EMPLOYEE_RECORD_FORMAT = 'i 10s 30s 30s 1s 10s' 

# employee_id(int),department_id (char[4]),from_date(char[10]),to_date(char[10])
DEPARTMENT_RECORD_FORMAT = 'i 4s 10s 10s' 

db_employee = HeapFile("data/deparment_employee.bin", DEPARTMENT_RECORD_FORMAT, PAGE_SIZE)

db_employee.export_to_heap("data/deparment_employee.csv")

print(f"Páginas generadas: {db_employee.count_pages()}")