import re


def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def split_sections(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    pattern = r'(Abschnitt [IVXLCDM]+)'

    sections = re.split(pattern, content)
    sections = [sections[i] + sections[i + 1] for i in range(1, len(sections), 2)]

    for section in sections:
        section_title: str = section.split(':')[0]
        section = section.replace("\n \n \n", "\n\n").replace(" \n", "\n")
        file_name = f'{section_title}.txt'

        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(section)

def paragraphs_chunks(sect: dict) -> list[str]:
    documents = []

    for _ , sec in sect.items():
        for item in parse_paragraph(sec):
            documents.append(item)
    
    return documents

def parse_paragraph(text: str) -> list[str]:
    lines = text.split('\n\n')

    chunks = []
    current_chunk = ""

    for line in lines:
        if line.startswith('§'):
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line
        else:
            current_chunk += " " + line

    if current_chunk:
        chunks.append(current_chunk.strip())
    chunks[0] = chunks[0] + " " + chunks[1]
    chunks.remove(chunks[1])
    return chunks