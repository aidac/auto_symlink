import os
import re
import time

source_directories = {
    '/lake/torrents/shows': '/lake/tv',
    '/lake/torrents/movies': '/lake/movies'
}

def format_dir_name(name):
    # Remove known irrelevant patterns and extensions
    name = re.sub(r'\[.*?\]\s*', '', name)  # Remove bracketed patterns
    name = re.sub(r'\(.+\)$', '', name).strip()  # Remove parentheses at the end
    # Replace dots, underscores, and spaces with a single space for uniformity
    formatted_name = re.sub(r'[._ ]+', ' ', name)
    print(f"Parsed source name: '{name}' -> '{formatted_name}'")
    return formatted_name

def get_existing_dirs(base_dir):
    return {dir_name for dir_name in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, dir_name))}

def find_year(name):
    match = re.search(r'\b(19[0-9]{2}|20[0-9]{2})\b', name)
    return match.group(0) if match else None

def match_directory(formatted_name, existing_dirs):
    # Match with and without the year
    name_parts = formatted_name.split()
    year = find_year(formatted_name)

    for i in range(len(name_parts), 0, -1):
        partial_name = ' '.join(name_parts[:i])
        for dir_name in existing_dirs:
            if partial_name in dir_name and (year is None or year in dir_name):
                return dir_name

    for i in range(len(name_parts), 0, -1):
        partial_name = ' '.join(name_parts[:i])
        for dir_name in existing_dirs:
            if partial_name in dir_name:
                return dir_name
    return None

def create_symlink_with_retries(source, destination, max_retries=1, retry_interval=30):
    attempt = 0
    while attempt < max_retries:
        try:
            if not os.path.exists(destination):
                os.symlink(source, destination)
                print(f"Symlink created: {source} -> {destination}")
                return
            else:
                print(f"Symlink already exists for {source}")
                return
        except Exception as e:
            print(f"Failed to create symlink on attempt {attempt + 1}: {e}")
            time.sleep(retry_interval)
            attempt += 1
    print(f"Failed to create symlink after {max_retries} attempts.")

def scan_directories(seen_items):
    while True:
        for source_base, dest_base in source_directories.items():
            current_items = set(os.listdir(source_base))
            new_items = current_items - seen_items[source_base]
            seen_items[source_base] = current_items

            existing_dirs = get_existing_dirs(dest_base)

            for item in new_items:
                item_path = os.path.join(source_base, item)
                if os.path.isdir(item_path):
                    dest_dir = dest_base + ('-uhd' if '2160p' in item else '')
                    formatted_name = format_dir_name(item)
                    matching_dir = match_directory(formatted_name, existing_dirs)
                    
                    if matching_dir:
                        full_dest_path = os.path.join(dest_dir, matching_dir, os.path.basename(item_path))
                        print(f"Match found: '{item}' -> '{full_dest_path}'")
                        create_symlink_with_retries(item_path, full_dest_path)
                    else:
                        print(f"No match found for '{item}' in '{dest_dir}'")

        time.sleep(10)  # Interval for scanning the directories

if __name__ == "__main__":
    seen_items = {path: set(os.listdir(path)) for path in source_directories.keys()}
    scan_directories(seen_items)
