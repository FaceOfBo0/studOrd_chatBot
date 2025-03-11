import re

def paragraphs_chunks(sect: dict) -> list[str]:
    """Legacy method for compatibility"""
    documents = []
    for _, sec in sect.items():
        for item in parse_paragraphs(sec):
            documents.append(item)
    return documents


def parse_paragraphs(text: str) -> list[str]:
        """Legacy method for compatibility"""
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


def parse_sentences(text: str) -> list[str]:
    """Split text into sentences, handling abbreviations and special cases"""
    if not text or len(text.strip()) < 2:  # Ignore very short texts
        return []

    # Replace newlines with spaces for better sentence detection
    text = re.sub(r'\s+', ' ', text)

    # First protect URLs by replacing them with markers
    url_pattern = r'(?:http[s]?://)?(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z-]+)+(?:/[^\s]*)?'
    text = re.sub(url_pattern, lambda m: f"URL_{m.group().replace('.', '_DOT_')}", text)

    # Replace dates with month names to protect them
    month_pattern = r'(\d{1,2})\.\s*(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)'
    text = re.sub(month_pattern, lambda m: f"DATE_{m.group(1)}_{m.group(2)}", text)

    # Replace semester enumerations
    semester_pattern = r'(\d+)\.\s*Semester'
    text = re.sub(semester_pattern, lambda m: f"SEM_{m.group(1)}_SEMESTER", text)

    # Replace Abs. in all contexts (both with and without preceding paragraph numbers)
    text = re.sub(r'((?:§\s*\d+\s*)?Abs)\.(\s*\d*)', r'\1_MARKER\2', text)

    # Replace vgl. references to protect them
    text = re.sub(r'(\(?\s*)vgl\.(\s*(?:§\s*\d+|[^.!?])*)', r'\1VGL_MARKER\2', text)

    # Replace common abbreviations that shouldn't end sentences
    abbrev_patterns = [
        (r'(\s+|^)ggf\.(\s+|$)', r'\1GGF_MARKER\2'),
        (r'(?:\(?\s*)z\.B\.(?:\s*(?:[^.!?])*?)(?=\)|\.)', r'ZB_MARKER'),  # Updated z.B. pattern
        (r'(\s+|^)bzw\.(\s+|$)', r'\1BZW_MARKER\2'),
        (r'(\s+|^)etc\.(\s+|$)', r'\1ETC_MARKER\2'),
        (r'(\s+|^)gem\.(\s+|$)', r'\1GEM_MARKER\2'),
        (r'(\s+|^)u\.a\.(\s+|$)', r'\1UA_MARKER\2'),
        (r'(\s+|^)Nr\.(\s+|$)', r'\1NR_MARKER\2'),
        (r'(\s+|^)i\.V\.(\s+|$)', r'\1IV_MARKER\2'),
    ]
    for pattern, repl in abbrev_patterns:
        text = re.sub(pattern, repl, text)

    # Common abbreviations in the study regulations (as fallback)
    abbreviations = (r'(?<!z\.B)(?<!bzw)(?<!etc)(?<!Abs)(?<!Nr)(?<!gem)(?<!vgl)(?<!ggf)(?<!u\.a)(?<!i\.V)'
                    # Handle single-digit dates (e.g., 1.)
                    r'(?<!0\.)(?<!1\.)(?<!2\.)(?<!3\.)(?<!4\.)(?<!5\.)(?<!6\.)(?<!7\.)(?<!8\.)(?<!9\.)'
                    # Handle two-digit dates (e.g., 31.)
                    r'(?<!00\.)(?<!01\.)(?<!02\.)(?<!03\.)(?<!04\.)(?<!05\.)(?<!06\.)(?<!07\.)(?<!08\.)(?<!09\.)'
                    r'(?<!10\.)(?<!11\.)(?<!12\.)(?<!13\.)(?<!14\.)(?<!15\.)(?<!16\.)(?<!17\.)(?<!18\.)(?<!19\.)'
                    r'(?<!20\.)(?<!21\.)(?<!22\.)(?<!23\.)(?<!24\.)(?<!25\.)(?<!26\.)(?<!27\.)(?<!28\.)(?<!29\.)'
                    r'(?<!30\.)(?<!31\.)'
                    )

    # Pattern for sentence splitting, considering abbreviations and requiring minimum structure
    sentence_pattern = fr'{abbreviations}([^.!?]*[.!?])(?:\s+|\Z)'

    # Split into potential sentences using finditer
    potential_sentences = re.finditer(sentence_pattern, text, re.DOTALL)

    # Filter and clean sentences
    sentences = []
    for match in potential_sentences:
        s = match.group(1).strip()

        # Skip if the sentence starts with a marker
        if s.startswith(('DATE_', 'URL_', 'SEM_')):
            continue

        # Restore URLs
        s = re.sub(r'URL_([^_]+(?:_DOT_[^_]+)*)',
                    lambda m: m.group(1).replace('_DOT_', '.'), s)

        # Restore any date markers back to their original form
        s = re.sub(r'DATE_(\d{1,2})_([^_]+)', r'\1. \2', s)

        # Restore semester markers
        s = re.sub(r'SEM_(\d+)_SEMESTER', r'\1. Semester', s)

        # Restore Abs. markers
        s = re.sub(r'Abs_MARKER', 'Abs.', s)

        # Restore vgl. markers
        s = re.sub(r'VGL_MARKER', 'vgl.', s)

        # Restore other abbreviation markers
        abbrev_restorations = {
            'GGF_MARKER': 'ggf.',
            'ZB_MARKER': 'z.B.',
            'BZW_MARKER': 'bzw.',
            'ETC_MARKER': 'etc.',
            'GEM_MARKER': 'gem.',
            'UA_MARKER': 'u.a.',
            'NR_MARKER': 'Nr.',
            'IV_MARKER': 'i.V.'
        }
        for marker, original in abbrev_restorations.items():
            s = s.replace(marker, original)

        # Only keep strings that:
        # 1. Are longer than 5 characters
        # 2. Contain at least one word character
        # 3. Are not just special characters or single letters
        # 4. Don't start with numbers followed by period
        if (len(s) > 5 and
            re.search(r'\w', s) and
            not re.match(r'^[^a-zA-Z]*$', s) and
            not re.match(r'^[a-zA-Z]$', s) and
            not re.match(r'^\d+\.', s)):
            sentences.append(s)

    return sentences