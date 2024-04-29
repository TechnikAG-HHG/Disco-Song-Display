import os

def remove_duplicate_lines(filename):
    lines_seen = set()  # Set to store unique lines

    with open(filename, 'r') as file:
        lines = file.readlines()

    with open(filename, 'w') as file:
        for line in lines:
            if line not in lines_seen:
                file.write(line)
                lines_seen.add(line)
            else:
                print(line)

    print(f"Duplicate lines removed from {filename}.")


# Usage
filename = '../Flask_Server/blacklist.txt'  # Replace with the actual filename
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, filename)

remove_duplicate_lines(file_path)
