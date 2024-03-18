import sys
import requests
import time
from multiprocessing import Process, Queue

def read_file(file_name):
    words = []
    with open(file_name, 'r') as file:
        for line in file:
            words.append(line.strip())
    return words

def divide_into_chunks(lst, size):
    chunks = []
    for i in range(0, len(lst), size):
        chunks.append(lst[i:i+size])
    return chunks

def get_valid_paths(words, base_url):
    existing_paths = []
    for word in words:
        to_check = base_url + word
        response = requests.get(to_check)
        status_code = response.status_code
        if status_code != 404:
            existing_paths.append((to_check, f"Status Code: {status_code}"))
    return existing_paths

def process_chunk(q, base_url, chunk):
    results = get_valid_paths(chunk, base_url)
    q.put(results)

def execute_in_multithreading(word_list_file_path, base_url):
    start_time = time.time()

    print("We are checking the possible paths for the target, please wait until the end...")

    word_list = read_file(word_list_file_path)
    chunks = divide_into_chunks(word_list, 500)
    q = Queue()
    processes = []

    for chunk in chunks:
        p = Process(target=process_chunk, args=(q, base_url, chunk))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    while not q.empty():
        results = q.get()
        for url, status_code in results:
            print(f"URL: {url}, {status_code}")

    print(f"Execution time: {time.time() - start_time} seconds")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python script.py <file-path> <target-base-url>")
        sys.exit(1)

    base_url = sys.argv[2]
    file_path = sys.argv[1]
        
    execute_in_multithreading(file_path, base_url)
