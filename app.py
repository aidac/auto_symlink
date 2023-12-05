import os
import re
import time

# Environment variables
source_directory_shows = os.environ.get('SOURCE_DIRECTORY_SHOWS', '/default/source/shows')
source_directory_movies = os.environ.get('SOURCE_DIRECTORY_MOVIES', '/default/source/movies')
destination_directory_shows = os.environ.get('DESTINATION_DIRECTORY_SHOWS', '/default/destination/tv')
destination_directory_movies = os.environ.get('DESTINATION_DIRECTORY_MOVIES', '/default/destination/movies')
destination_directory_uhd_shows = os.environ.get('DESTINATION_DIRECTORY_UHD_SHOWS', destination_directory_shows)
destination_directory_uhd_movies = os.environ.get('DESTINATION_DIRECTORY_UHD_MOVIES', destination_directory_movies)
uhd_library = os.environ.get('UHD_LIBRARY', 'True').lower() == 'true'

source_directories = {
    source_directory_shows: destination_directory_shows,
    source_directory_movies: destination_directory_movies
}


def create_symlinks_for_files_in_folder(source_folder, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    for file in os.listdir(source_folder):
        source_file = os.path.join(source_folder, file)
        destination_file = os.path.join(destination_folder, file)
        if not os.path.exists(destination_file):
            os.symlink(source_file, destination_file)
            print(f"Symlink created: {source_file} -> {destination_file}")

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
            # Determine if current item is UHD and adjust destination directory accordingly
            dest_base_uhd = dest_base
            if uhd_library and '-uhd' in dest_base:
                if 'shows' in source_base:
                    dest_base_uhd = destination_directory_uhd_shows
                elif 'movies' in source_base:
                    dest_base_uhd = destination_directory_uhd_movies
                continue

            current_items = set(os.listdir(source_base))
            new_items = current_items - seen_items[source_base]
            seen_items[source_base] = current_items

            existing_dirs = get_existing_dirs(dest_base)

            for item in new_items:
                item_path = os.path.join(source_base, item)
                if os.path.isfile(item_path):
                    # If item is a file, link it directly
                    dest_dir = dest_base + ('-uhd' if uhd_library and '2160p' in item else '')
                    formatted_name = format_dir_name(item)
                    matching_dir = match_directory(formatted_name, existing_dirs)

                    if matching_dir:
                        destination_file = os.path.join(dest_dir, matching_dir, os.path.basename(item_path))
                        create_symlink_with_retries(item_path, destination_file)
                        print(f"File symlink created: '{item_path}' -> '{destination_file}'")
                    else:
                        print(f"No match found for file '{item}' in '{dest_dir}'")

                elif os.path.isdir(item_path):
                    # If item is a folder, recreate folder and link files inside it
                    dest_dir = dest_base + ('-uhd' if uhd_library and '2160p' in item else '')
                    formatted_name = format_dir_name(item)
                    matching_dir = match_directory(formatted_name, existing_dirs)

                    if matching_dir:
                        destination_folder = os.path.join(dest_dir, matching_dir, os.path.basename(item_path))
                        create_symlinks_for_files_in_folder(item_path, destination_folder)
                        print(f"Folder processed with file symlinks: '{item_path}' -> '{destination_folder}'")
                    else:
                        print(f"No match found for folder '{item}' in '{dest_dir}'")

        time.sleep(10)  # Interval for scanning the directories

if __name__ == "__main__":
    seen_items = {path: set(os.listdir(path)) for path in source_directories.keys()}
    scan_directories(seen_items)