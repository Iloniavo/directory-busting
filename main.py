import threading
import sys
import requests
import time

def read_file(file_name):
    """
    This function reads a text file containing a list of words.
    :param file_name: The name of the text file.
    :return: The list of words.
    """
    words = []
    with open(file_name, 'r') as file:
        for line in file:
            words.append(line.strip())  # Remove newline characters
    return words

def divide_into_chunks(lst, size):
    """
    This function divides a list into chunks of the specified size.
    :param lst: The list to divide.
    :param size: The size of each chunk.
    :return: A list of chunks.
    """
    chunks = []
    for i in range(0, len(lst), size):
        chunks.append(lst[i:i+size])
    return chunks

def process_chunk(valid_paths, lock, base_url, chunk):
    """
    This function processes a chunk of the word list in multi-threading.
    :param valid_paths: List of words which match to the url
    :param lock: Lock for multiprocessing 
    :param base_url: base_url of the target 
    :param chunk: The chunk of the word list.
    """
    with lock:
        valid_paths.extend(get_valid_paths(chunk, base_url))


def execute_in_multithreading(word_list_file_path, base_url):
    """
    This function executes the specified function in multi-threading on chunks of the given list.
    :param lst: The list to process.
    :param func: The function to execute on each chunk.
    :param chunk_size: The size of each chunk.
    """
    start_time = time.time()

    word_list = read_file(word_list_file_path)
    chunks = divide_into_chunks(word_list, int(500))
    threads = []
    result_list = []
    lock = threading.Lock()
    print("The program is checking the unprotected paths related to "+ base_url)
    for chunk in chunks:
        thread = threading.Thread(target=process_chunk, args=(result_list, lock, base_url, chunk))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
        
    for url, status_code in result_list:
        print(f"URL: {url}, {status_code}")

def get_valid_paths(words, base_url):
    """
    Check the valid paths and add into a list
    :param words: List of words
    :param base_url: Base url to test
    """
    existing_paths = []
    for word in words:
        to_check = base_url + word
        response = requests.get(to_check)
        status_code = response.status_code
        if status_code != 404:
            existing_paths.append((to_check, f"Status Code: {status_code}"))
    return existing_paths

if __name__ == '__main__':
    """
    Main function of the program
    """
    if len(sys.argv) != 3:
        print("Usage: python script.py <wordlist_file> <base_url>")
        sys.exit(1)

    base_url =  sys.argv[1]
    file_path = sys.argv[2]
        
    execute_in_multithreading("./directories.txt", "http://127.0.0.1:5000/")
