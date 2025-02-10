import os

def saveStrToFile(data: str, file_name: str, enc: str):
    with open(file_name, 'w', encoding=enc) as file:
        file.write(data)

def read_files(directory: str) -> dict:
    files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    files.insert(9,files[4])
    files.remove(files[4])

    sections = {}
    for i,file_name in enumerate(files):
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            sections[i+1] = file.read()
    return sections