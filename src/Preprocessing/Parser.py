import re

def paragraphs_chunks(sect: dict) -> list[str]:
    """Convert section dictionary into a list of paragraph chunks.
    
    Args:
        sect: Dictionary containing section data.
        
    Returns:
        List of paragraph chunks as strings.
    """
    documents = []
    for _, sec in sect.items():
        for item in parse_paragraphs(sec):
            documents.append(item)
    return documents


def parse_paragraphs(text: str) -> list[str]:
    """Parse text into paragraph chunks, handling section markers and content.
    
    Args:
        text: The input text to parse.
        
    Returns:
        List of parsed paragraph chunks.
    """
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
    if len(chunks) > 1:
        chunks[0] = chunks[0] + " " + chunks[1]
        chunks.remove(chunks[1])
    return chunks


def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace.
    
    Args:
        text: The text to clean.
        
    Returns:
        Cleaned text with normalized whitespace.
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def split_sections(file_path: str):
    """Split a file into sections based on section markers and save them as separate files.
    
    Args:
        file_path: Path to the file containing multiple sections.
    """
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
