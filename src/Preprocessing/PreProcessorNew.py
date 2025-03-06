from dataclasses import dataclass, asdict
from typing import List, Optional, Dict
import re
from pathlib import Path
from Preprocessing import FileHandler
import glob
import json
from typing import Any

@dataclass
class SubPoint:
    number: str
    content: str

@dataclass
class Point:
    number: str
    content: str
    subpoints: List[SubPoint]

@dataclass
class Paragraph:
    number: str
    title: Optional[str]
    content: str
    points: List[Point]

@dataclass
class Section:
    number: str
    title: str
    paragraphs: List[Paragraph]

@dataclass
class StudyRegulation:
    sections: List[Section]


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


def parse_subpoints(text: str) -> List[SubPoint]:
    # Match both formats: a) and (a), but only at the start of a line or after a clear separator
    subpoint_pattern = r'(?:^|\n)\s*(?:(\d+)\.|\(([a-z])\)|([a-z]\))\s*)(.*?)(?=(?:(?:^|\n)\s*(?:\d+\.|\([a-z]\)|[a-z]\))|$))'
    subpoints = []
    for match in re.finditer(subpoint_pattern, text, re.DOTALL):
        # Get number or letter (from either format)
        number = match.group(1) or match.group(2) or match.group(3).rstrip(')')
        content = match.group(4)
        
        # Skip if this looks like part of a word (e.g., "...ung)")
        if len(number) > 1 or not content.strip():
            continue
            
        subpoints.append(SubPoint(
            number=number,
            content=content.strip()
        ))
    return subpoints


def parse_points(text: str) -> List[Point]:
    # Only match points in (1) format
    point_pattern = r'\((\d+)\)\s*(.*?)(?=(?:\(\d+\)|$))'
    points = []
    for match in re.finditer(point_pattern, text, re.DOTALL):
        number, content = match.groups()
        
        # Parse subpoints (now including numbered format)
        subpoints = parse_subpoints(content)
        if subpoints:
            # Remove subpoint text from content
            content = re.sub(r'(?:\d+\.|[a-z]\)).*?(?=(?:\d+\.|[a-z]\)|$))', '', content, flags=re.DOTALL)
        
        points.append(Point(
            number=number,
            content=content.strip(),
            subpoints=subpoints
        ))
    return points


def parse_paragraphs(text: str) -> List[Paragraph]:
    # Updated pattern to handle different RO reference formats
    para_pattern = r'(?:^|\n\n|\n(?=§))§\s*(\d+)\s+([^(\n]+(?:\([^)]+\)[^(\n]+)*?)(?:\((RO:?\s*(?:§\s*)?\d+)\))?\s*\n+(.*?)(?=(?:\n\n|\n(?=§))§\s*\d+(?:\s+(?!Abs))|$)'
    paragraphs = []
    
    for match in re.finditer(para_pattern, text, re.DOTALL):
        number, title_text, ro_ref, content = match.groups()
        
        # Combine title and RO reference
        title = title_text.strip()
        if ro_ref:
            title = f"{title} ({ro_ref})"
        
        # Parse points from content
        points = parse_points(content)
        
        # If points were found, remove their text from the content
        if points:
            # Remove numbered points from content
            content = re.sub(r'\(\d+\).*?(?=\(\d+\)|$)', '', content, flags=re.DOTALL).strip()
        
        # Only keep content if it's not just whitespace after removing points
        content = content.strip()
        if not content and points:
            content = ""
        
        paragraphs.append(Paragraph(
            number=number,
            title=title,
            content=content,
            points=points
        ))
    return paragraphs


def parse_section(text: str) -> Section:
    section_match = re.match(r'Abschnitt ([IVXLCDM]+):\s*(.*?)(?=\n\s*§)', text, re.DOTALL)
    if not section_match:
        raise ValueError("Invalid section format")
    
    number, title = section_match.groups()
    paragraphs = parse_paragraphs(text)
    
    return Section(number=number, title=title.strip(), paragraphs=paragraphs)


def process_regulation() -> StudyRegulation:
    """Processes all section files and returns a structured StudyRegulation"""
    # Read all section files
    sections_dict = FileHandler.read_files("src/data/sections")
    
    # Parse each section
    sections = []
    for section_title in sorted(sections_dict.keys()):  # Sort to maintain order
        section = parse_section(sections_dict[section_title])
        sections.append(section)
    
    return StudyRegulation(sections=sections)


def save_regulation_to_json(regulation: StudyRegulation, file_path: str) -> None:
    """Serializes the StudyRegulation to JSON and saves it to a file"""
    def encode_dataclass(obj: Any) -> dict:
        if hasattr(obj, '__dataclass_fields__'):
            return {
                '_type': obj.__class__.__name__,
                'data': asdict(obj)
            }
        raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(regulation, f, default=encode_dataclass, ensure_ascii=False, indent=2)


def load_regulation_from_json(file_path: str) -> StudyRegulation:
    """Deserializes the StudyRegulation from a JSON file"""
    def decode_dataclass(obj_dict: dict) -> Any:
        if '_type' not in obj_dict:
            return obj_dict

        obj_type = obj_dict['_type']
        data = obj_dict['data']

        if obj_type == 'StudyRegulation':
            sections = [decode_dataclass({'_type': 'Section', 'data': s}) for s in data['sections']]
            return StudyRegulation(sections=sections)
        
        elif obj_type == 'Section':
            paragraphs = [decode_dataclass({'_type': 'Paragraph', 'data': p}) for p in data['paragraphs']]
            return Section(
                number=data['number'],
                title=data['title'],
                paragraphs=paragraphs
            )
        
        elif obj_type == 'Paragraph':
            points = [decode_dataclass({'_type': 'Point', 'data': p}) for p in data['points']]
            return Paragraph(
                number=data['number'],
                title=data['title'],
                content=data['content'],
                points=points
            )
        
        elif obj_type == 'Point':
            subpoints = [decode_dataclass({'_type': 'SubPoint', 'data': sp}) for sp in data['subpoints']]
            return Point(
                number=data['number'],
                content=data['content'],
                subpoints=subpoints
            )
        
        elif obj_type == 'SubPoint':
            return SubPoint(
                number=data['number'],
                content=data['content']
            )
        
        return obj_dict

    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        return decode_dataclass(json_data)


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


def create_sentence_context_map(json_file_path: str) -> Dict[str, Dict[str, str]]:
    """Creates a map of sentences to their context from a study regulation JSON file"""
    # Load the study regulation from JSON
    regulation = load_regulation_from_json(json_file_path)
    sentence_map = {}

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
                    sentence_map[sentence] = {
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
                    for sentence in sentences:
                        sentence_map[sentence] = point_context.copy()

                # Process subpoints
                for subpoint in point.subpoints:
                    subpoint_context = {
                        **point_context,
                        'subpoint_number': subpoint.number
                    }

                    if subpoint.content:
                        sentences = parse_sentences(subpoint.content)
                        for sentence in sentences:
                            sentence_map[sentence] = subpoint_context.copy()

    return sentence_map


def get_context_string(context: Dict[str, str]) -> str:
    """Helper function to format context information as a readable string"""
    parts = [
        f"Abschnitt {context['section_number']}: {context['section_title']}",
        f"§ {context['paragraph_number']}: {context['paragraph_title']}"
    ]
    
    if context['point_number']:
        parts.append(f"Point ({context['point_number']})")
        
    if context['subpoint_number']:
        parts.append(f"Subpoint {context['subpoint_number']})")
        
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