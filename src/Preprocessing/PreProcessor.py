from typing import Dict
from . import FileHandler, Parser
from data.StudyRegulation import StudyRegulation
from data.StudyRegulation import parse_section, parse_section_without_subpoints
from data.Module import Module
import os


def get_modules_from_csv(mods_dir: str) -> list[Module]:
    """Retrieve and parse all module information from CSV files in the specified directory.
    
    Args:
        mods_dir: Path to the directory containing module CSV files.
        
    Returns:
        A list of Module objects.
    """
    files = sorted([f for f in os.listdir(mods_dir) if f.endswith('.csv')])
    list_mods = []

    for i, file_name in enumerate(files):
        file_path = os.path.join(mods_dir, file_name)
        with open(file_path, "r", encoding="utf-8") as file:
            list_mods.append(Module(file))

    return list_mods

def process_regulation(files_path: str) -> StudyRegulation:
    """Process all section files and create a structured StudyRegulation object.
    
    Args:
        files_path: Path to the directory containing section files.
        
    Returns:
        A StudyRegulation object containing all parsed sections.
    """
    # Read all section files
    sections_dict = FileHandler.read_section_files(files_path)

    # Parse each section
    sections = []
    for section_title in sorted(sections_dict.keys()):  # Sort to maintain order
        section = parse_section(sections_dict[section_title])
        sections.append(section)

    return StudyRegulation(sections=sections)

def get_context_string(context: Dict[str, str]) -> str:
    """Format context information into a readable string.
    
    Args:
        context: Dictionary containing section, paragraph and point information.
        
    Returns:
        A formatted string representing the context.
    """
    parts = [
        f"Abschnitt {context['section_number']}",
        f"§ {context['paragraph_number']}"
    ]

    if context['point_number']:
        parts.append(f"Absatz {context['point_number']}")

    if context['subpoint_number']:
        parts.append(f"Punkt {context['subpoint_number']}")

    return ", ".join(parts)


def process_regulation_wo_subpoints(files_path: str) -> StudyRegulation:
    """Process section files and create a StudyRegulation object without subpoints.
    
    Args:
        files_path: Path to the directory containing section files.
        
    Returns:
        A StudyRegulation object containing parsed sections without subpoints.
    """
    # Read all section files
    sections_dict = FileHandler.read_section_files(files_path)

    # Parse each section
    sections = []
    for section_title in sorted(sections_dict.keys()):  # Sort to maintain order
        section = parse_section_without_subpoints(sections_dict[section_title])
        sections.append(section)

    return StudyRegulation(sections=sections)


def create_pntCtxMap_from_stdyReg(regulation: StudyRegulation) -> Dict[str, Dict[str, str]]:
    """Create a map of points of the study regulation to their context information from a StudyRegulation.
    
    This version does not consider subpoints. If a paragraph has points, each point becomes a key.
    If a paragraph has no points, its content becomes a key.
    
    Args:
        regulation: A StudyRegulation object to process.
        
    Returns:
        A dictionary mapping study regulation points to their context information.
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

    return point_map

def paragraphs_chunks(sect: dict) -> list[str]:
    """Extract paragraph chunks from a section dictionary.
    
    Args:
        sect: Dictionary containing section data.
        
    Returns:
        A list of paragraph chunks as strings.
    """
    documents = []

    for _ , sec in sect.items():
        for item in parse_paragraph(sec):
            documents.append(item)
    
    return documents

def parse_paragraph(text: str) -> list[str]:
    """Parse a text into paragraph chunks.
    
    Args:
        text: The input text to parse.
        
    Returns:
        A list of paragraph chunks.
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
    chunks[0] = chunks[0] + " " + chunks[1]
    chunks.remove(chunks[1])
    return chunks
