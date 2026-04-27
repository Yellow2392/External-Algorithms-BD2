import matplotlib.pyplot as plt
import pandas as pd
from external_sort import ExternalSort
from external_hashing import ExternalHashing

def run_benchmarks():
    PAGE_SIZE = 4096
    BUFFER_SIZES = [65536, 131072, 262144]  # 64KB, 128KB, 256KB
    results_sort = []
    results_hash = []
    
    DEPT_FORMAT = 'i4s10s10s'
    INDEX_FROM_DATE = 2 

    for b_size in BUFFER_SIZES:
        m_pages = b_size // PAGE_SIZE
        print(f"\n--- Probando con {b_size//1024} KB ({m_pages} páginas) ---")

        # External sort
        sorter = ExternalSort(record_format=DEPT_FORMAT, page_size=PAGE_SIZE, buffer_size=b_size)
        res_s = sorter.external_sort("data/deparment_employee.bin", "data/deparment_employee_sorted.bin", sort_key_index=INDEX_FROM_DATE)
        res_s['buffer_label'] = f"{b_size//1024} KB"
        results_sort.append(res_s)

        # External hashing
        hasher = ExternalHashing(recordformat=DEPT_FORMAT, pagesize=PAGE_SIZE, buffersize=b_size)
        res_h = hasher.externalhashgroupby("data/deparment_employee.bin", groupkeyindex=INDEX_FROM_DATE)
        res_h['buffer_label'] = f"{b_size//1024} KB"
        results_hash.append(res_h)
        
        print(f"SORT | Runs: {res_s['runs_generated']} | Time: {res_s['time_total_sec']}s | I/O: {res_s['pages_read'] + res_s['pages_written']}")
        print(f"HASH | Part: {res_h['partitionscreated']} | Time: {res_h['timetotalsec']}s | I/O: {res_h['pagesread'] + res_h['pageswritten']}")

    plot_performance(results_sort, results_hash)
    
    return results_sort, results_hash

def plot_performance(sort_data, hash_data):
    labels = [d['buffer_label'] for d in sort_data]
    sort_times = [d['time_total_sec'] for d in sort_data]
    hash_times = [d['timetotalsec'] for d in hash_data]

    plt.figure(figsize=(10, 6))
    plt.plot(labels, sort_times, marker='o', label='External Sort')
    plt.plot(labels, hash_times, marker='s', label='External Hashing')
    plt.title('Tiempo Total vs. BUFFER_SIZE')
    plt.xlabel('Buffer Size')
    plt.ylabel('Tiempo (segundos)')
    plt.legend()
    plt.grid(True)
    plt.savefig('performance_graph.png')
    plt.show()

if __name__ == "__main__":
    run_benchmarks()