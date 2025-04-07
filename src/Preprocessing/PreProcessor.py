from typing import Dict
from . import FileHandler, Parser
from data.StudyRegulation import StudyRegulation
from data.StudyRegulation import parse_section, parse_section_without_subpoints
from data.Module import Module
import os


def get_modules_from_csv(mods_dir: str) -> list[Module]:
    files = sorted([f for f in os.listdir(mods_dir) if f.endswith('.csv')])
    list_mods = []

    for i, file_name in enumerate(files):
        file_path = os.path.join(mods_dir, file_name)
        with open(file_path, "r", encoding="utf-8") as file:
            list_mods.append(Module(file))

    return list_mods

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


def create_sntCtxMap_list(json_file_path: str) -> list[tuple[str, Dict[str, str]]]:
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
                sentences = Parser.parse_sentences(para.content)
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
                    sentences = Parser.parse_sentences(point.content)
                    for sentence in sentences:
                        sentence_list.append((sentence, point_context.copy()))

                # Process subpoints
                for subpoint in point.subpoints:
                    subpoint_context = {
                        **point_context,
                        'subpoint_number': subpoint.number
                    }

                    if subpoint.content:
                        sentences = Parser.parse_sentences(subpoint.content)
                        for sentence in sentences:
                            sentence_list.append((sentence, subpoint_context.copy()))

    return sentence_list


def get_context_string(context: Dict[str, str]) -> str:
    """Helper function to format context information as a readable string"""
    parts = [
        f"Abschnitt {context['section_number']}",
        f"§ {context['paragraph_number']}"
    ]

    if context['point_number']:
        parts.append(f"Absatz {context['point_number']}")

    if context['subpoint_number']:
        parts.append(f"Punkt {context['subpoint_number']}")

    return ", ".join(parts)


def create_pntCtxMap(sentence_list: list[tuple[str, Dict[str, str]]]) -> Dict[str, Dict[str, str]]:
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
                # sentences = Parser.parse_sentences(para.content)
                # concatenated_text = ' '.join(sentences)
                point_map[para.content] = {
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
                    point_map[point.content] = point_context
                    #sentences = Parser.parse_sentences(point.content)
                    #concatenated_text = ' '.join(sentences)
                    #point_map[concatenated_text] = point_context

    return point_map

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
