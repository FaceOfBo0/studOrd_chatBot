from typing import Dict, List
import re
from pathlib import Path
from . import FileHandler
from data.StudyRegulation import StudyRegulation
from data.StudyRegulation import parse_section, parse_section_without_subpoints
import glob

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


def split_sections_v2(file_path: str) -> Dict[str, str]:
    """Splits original file into sections and saves them as separate files"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    pattern = r'(Abschnitt [IVXLCDM]+)'
    sections = re.split(pattern, content)
    sections = [sections[i] + sections[i + 1] for i in range(1, len(sections), 2)]

    section_dict = {}
    for section in sections:
        section_title: str = section.split(':')[0]
        section = section.replace("\n \n \n", "\n\n").replace(" \n", "\n")
        file_name = f'{section_title}.txt'

        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(section)

        section_dict[section_title] = section

    return section_dict


def read_section_files() -> Dict[str, str]:
    """Reads all section files and returns their content"""
    section_dict = {}
    for file_path in glob.glob("Abschnitt*.txt"):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            section_title = Path(file_path).stem
            section_dict[section_title] = content
    return section_dict


def process_regulation(files_path: str) -> StudyRegulation:
    """Processes all section files and returns a structured StudyRegulation"""
    # Read all section files
    sections_dict = FileHandler.read_section_files(files_path)

    # Parse each section
    sections = []
    for section_title in sorted(sections_dict.keys()):  # Sort to maintain order
        section = parse_section(sections_dict[section_title])
        sections.append(section)

    return StudyRegulation(sections=sections)


def parse_sentences(text: str) -> List[str]:
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


def create_sntCtxMap_list(json_file_path: str) -> List[tuple[str, Dict[str, str]]]:
    """Creates an ordered list of sentences and their context from a study regulation JSON file"""
    # Load the study regulation from JSON
    regulation = FileHandler.load_regulation_from_json(json_file_path)
    sentence_list = []

    # Iterate through all sections
    for section in regulation.sections:
        section_context = {
            'section_number': section.number,
            'section_title': section.title
        }

        # Process paragraphs
        for para in section.paragraphs:
            para_context = {
                **section_context,
                'paragraph_number': para.number,
                'paragraph_title': para.title
            }

            # Process paragraph content
            if para.content:
                sentences = parse_sentences(para.content)
                for sentence in sentences:
                    sentence_list.append((sentence, {
                        **para_context,
                        'point_number': None,
                        'subpoint_number': None
                    }))

            # Process points
            for point in para.points:
                point_context = {
                    **para_context,
                    'point_number': point.number,
                    'subpoint_number': None
                }

                # Process point content
                if point.content:
                    sentences = parse_sentences(point.content)
                    for sentence in sentences:
                        sentence_list.append((sentence, point_context.copy()))

                # Process subpoints
                for subpoint in point.subpoints:
                    subpoint_context = {
                        **point_context,
                        'subpoint_number': subpoint.number
                    }

                    if subpoint.content:
                        sentences = parse_sentences(subpoint.content)
                        for sentence in sentences:
                            sentence_list.append((sentence, subpoint_context.copy()))

    return sentence_list


def get_context_string(context: Dict[str, str]) -> str:
    """Helper function to format context information as a readable string"""
    parts = [
        f"Abschnitt {context['section_number']}: {context['section_title']}",
        f"Paragraph {context['paragraph_number']}: {context['paragraph_title']}"
    ]

    if context['point_number']:
        parts.append(f"Absatz ({context['point_number']})")

    if context['subpoint_number']:
        parts.append(f"Punkt {context['subpoint_number']})")

    return " -> ".join(parts)


def paragraphs_chunks(sect: dict) -> list[str]:
    """Legacy method for compatibility"""
    documents = []
    for _, sec in sect.items():
        for item in parse_paragraph(sec):
            documents.append(item)
    return documents


def parse_paragraph(text: str) -> list[str]:
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


def create_pntCtxMap(sentence_list: List[tuple[str, Dict[str, str]]]) -> Dict[str, Dict[str, str]]:
    """Creates a map where keys are concatenated sentences belonging to the same point/paragraph
    and values are their context information.

    If a paragraph has points, each point (including its subpoints) becomes a key.
    If a paragraph has no points, its content becomes a key.

    Args:
        sentence_list: List of tuples containing (sentence, context) pairs in original order
    """
    point_map = {}
    temp_storage = {}

    # First, group sentences by their context while preserving order
    for sentence, context in sentence_list:
        # Create a unique key for the context
        if context['point_number']:
            # For points and subpoints, group under the point
            key = (context['section_number'], context['paragraph_number'], context['point_number'])
        else:
            # For paragraph content without points, group under the paragraph
            key = (context['section_number'], context['paragraph_number'])

        if key not in temp_storage:
            temp_storage[key] = {
                'sentences': [],
                'context': context
            }
        temp_storage[key]['sentences'].append(sentence)

    # Then create the final map with concatenated sentences as keys
    for key, value in temp_storage.items():
        # Keep sentences in original order (no sorting)
        concatenated_text = ' '.join(value['sentences'])

        # Store with the original context information
        point_map[concatenated_text] = value['context']

    return point_map


def process_regulation_wo_subpoints(files_path: str) -> StudyRegulation:
    """Processes all section files and returns a structured StudyRegulation without subpoints"""
    # Read all section files
    sections_dict = FileHandler.read_section_files(files_path)

    # Parse each section
    sections = []
    for section_title in sorted(sections_dict.keys()):  # Sort to maintain order
        section = parse_section_without_subpoints(sections_dict[section_title])
        sections.append(section)

    return StudyRegulation(sections=sections)


def create_pntCtxMap_from_stdyReg(regulation: StudyRegulation) -> Dict[str, Dict[str, str]]:
    """Creates a map where keys are concatenated sentences belonging to the same point/paragraph
    and values are their context information, without considering subpoints.

    If a paragraph has points, each point becomes a key.
    If a paragraph has no points, its content becomes a key.

    Args:
        regulation: A StudyRegulation object
    """
    point_map = {}

    # Iterate through all sections
    for section in regulation.sections:
        section_context = {
            'section_number': section.number,
            'section_title': section.title
        }

        # Process paragraphs
        for para in section.paragraphs:
            para_context = {
                **section_context,
                'paragraph_number': para.number,
                'paragraph_title': para.title
            }

            # Process paragraph content
            if para.content:
                sentences = parse_sentences(para.content)
                concatenated_text = ' '.join(sentences)
                point_map[concatenated_text] = {
                    **para_context,
                    'point_number': None,
                    'subpoint_number': None
                }

            # Process points
            for point in para.points:
                point_context = {
                    **para_context,
                    'point_number': point.number,
                    'subpoint_number': None
                }

                # Process point content
                if point.content:
                    sentences = parse_sentences(point.content)
                    concatenated_text = ' '.join(sentences)
                    point_map[concatenated_text] = point_context

    return point_map
