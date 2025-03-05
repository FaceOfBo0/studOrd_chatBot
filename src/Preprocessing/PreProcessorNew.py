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

class PreProcessorNew:
    @staticmethod
    def clean_text(text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def split_sections(file_path: str) -> Dict[str, str]:
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

    @staticmethod
    def read_section_files() -> Dict[str, str]:
        """Reads all section files and returns their content"""
        section_dict = {}
        for file_path in glob.glob("Abschnitt*.txt"):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                section_title = Path(file_path).stem
                section_dict[section_title] = content
        return section_dict

    @staticmethod
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

    @staticmethod
    def parse_points(text: str) -> List[Point]:
        # Only match points in (1) format
        point_pattern = r'\((\d+)\)\s*(.*?)(?=(?:\(\d+\)|$))'
        points = []
        for match in re.finditer(point_pattern, text, re.DOTALL):
            number, content = match.groups()
            
            # Parse subpoints (now including numbered format)
            subpoints = PreProcessorNew.parse_subpoints(content)
            if subpoints:
                # Remove subpoint text from content
                content = re.sub(r'(?:\d+\.|[a-z]\)).*?(?=(?:\d+\.|[a-z]\)|$))', '', content, flags=re.DOTALL)
            
            points.append(Point(
                number=number,
                content=content.strip(),
                subpoints=subpoints
            ))
        return points

    @staticmethod
    def parse_paragraphs(text: str) -> List[Paragraph]:
        # Updated pattern to only match proper paragraph headers
        para_pattern = r'(?:^|\n\n)§\s*(\d+)\s+([^(]+?)(?:\((RO:?\s*§\s*\d+)\))?\s*\n\n(.*?)(?=(?:\n\n§\s*\d+\s+[^A][^b][^s]|$))'
        paragraphs = []
        
        for match in re.finditer(para_pattern, text, re.DOTALL):
            number, title_text, ro_ref, content = match.groups()
            
            # Combine title and RO reference
            title = title_text.strip()
            if ro_ref:
                title = f"{title} ({ro_ref})"
            
            # Parse points from content
            points = PreProcessorNew.parse_points(content)
            
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

    @staticmethod
    def parse_section(text: str) -> Section:
        section_match = re.match(r'Abschnitt ([IVXLCDM]+):\s*(.*?)(?=\n\s*§)', text, re.DOTALL)
        if not section_match:
            raise ValueError("Invalid section format")
        
        number, title = section_match.groups()
        paragraphs = PreProcessorNew.parse_paragraphs(text)
        
        return Section(number=number, title=title.strip(), paragraphs=paragraphs)

    @staticmethod
    def process_regulation() -> StudyRegulation:
        """Processes all section files and returns a structured StudyRegulation"""
        # Read all section files
        # sections_dict = PreProcessorNew.read_section_files()
        sections_dict = FileHandler.read_files("src/data/sections")
        
        # Parse each section
        sections = []
        for section_title in sorted(sections_dict.keys()):  # Sort to maintain order
            section = PreProcessorNew.parse_section(sections_dict[section_title])
            sections.append(section)
        
        return StudyRegulation(sections=sections)
    
    @staticmethod
    def save_to_json(regulation: StudyRegulation, file_path: str) -> None:
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
    
    @staticmethod
    def load_from_json(file_path: str) -> StudyRegulation:
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

    @staticmethod
    def parse_sentences(text: str) -> List[str]:
        """Split text into sentences, handling abbreviations and special cases"""
        if not text or len(text.strip()) < 2:  # Ignore very short texts
            return []

        # Replace newlines with spaces for better sentence detection
        text = re.sub(r'\s+', ' ', text)
        
        # Common abbreviations in the study regulations
        abbreviations = r'(?<!z\.B)(?<!bzw)(?<!etc)(?<!Abs)(?<!Nr)(?<!gem)(?<!vgl)(?<!ggf)(?<!u\.a)'
        
        # Pattern for sentence splitting, considering abbreviations and requiring minimum sentence structure
        sentence_pattern = fr'{abbreviations}[.!?](?:\s+|\Z)'
        
        # Split into potential sentences
        potential_sentences = re.split(sentence_pattern, text)
        
        # Filter and clean sentences
        sentences = []
        for s in potential_sentences:
            s = s.strip()
            # Only keep strings that:
            # 1. Are longer than 5 characters
            # 2. Contain at least one word character
            # 3. Are not just special characters or single letters
            if (len(s) > 5 and 
                re.search(r'\w', s) and 
                not re.match(r'^[^a-zA-Z]*$', s) and
                not re.match(r'^[a-zA-Z]$', s)):
                sentences.append(s)
        
        return sentences

    @staticmethod
    def create_sentence_context_map(json_file_path: str) -> Dict[str, Dict[str, str]]:
        """Creates a map of sentences to their context from a study regulation JSON file"""
        # Load the study regulation from JSON
        regulation = PreProcessorNew.load_from_json(json_file_path)
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
                    sentences = PreProcessorNew.parse_sentences(para.content)
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
                        sentences = PreProcessorNew.parse_sentences(point.content)
                        for sentence in sentences:
                            sentence_map[sentence] = point_context.copy()

                    # Process subpoints
                    for subpoint in point.subpoints:
                        subpoint_context = {
                            **point_context,
                            'subpoint_number': subpoint.number
                        }

                        if subpoint.content:
                            sentences = PreProcessorNew.parse_sentences(subpoint.content)
                            for sentence in sentences:
                                sentence_map[sentence] = subpoint_context.copy()

        return sentence_map

    @staticmethod
    def get_context_string(context: Dict[str, str]) -> str:
        """Helper function to format context information as a readable string"""
        parts = [
            f"Section {context['section_number']}: {context['section_title']}",
            f"§{context['paragraph_number']}: {context['paragraph_title']}"
        ]
        
        if context['point_number']:
            parts.append(f"Point ({context['point_number']})")
            
        if context['subpoint_number']:
            parts.append(f"Subpoint {context['subpoint_number']})")
            
        return " -> ".join(parts)

def sections_chunks(sect: dict) -> list[str]:
    """Legacy method for compatibility"""
    documents = []
    for _, sec in sect.items():
        for item in paragraph_chunks(sec):
            documents.append(item)
    return documents

def paragraph_chunks(text: str) -> list[str]:
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