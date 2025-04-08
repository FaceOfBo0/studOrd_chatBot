import os
from typing import Any, Dict
from pathlib import Path
from dataclasses import asdict
import glob
from data.StudyRegulation import StudyRegulation, Section, Point, SubPoint, Paragraph
import json

def read_section_files_abs_alt() -> Dict[str, str]:
    """Read section files from the current directory and return their content.
    Path is beeing deduced from the file name
    
    Returns:
        A dictionary mapping section titles to their content.
    """
    
    section_dict = {}
    for file_path in glob.glob("Abschnitt*.txt"):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            section_title = Path(file_path).stem
            section_dict[section_title] = content
    return section_dict

def save_str_to_file(data: str, file_name: str, enc: str):
    """Save a string to a file with specified encoding.
    
    Args:
        data: The string content to save.
        file_name: The name of the file to save to.
        enc: The encoding to use when writing the file.
    """

    with open(file_name, 'w', encoding=enc) as file:
        file.write(data)

def read_section_files(directory: str) -> Dict[int, str]:
    """Read all section files from a directory and return their content.
    
    Args:
        directory: Path to the directory containing section files.
        
    Returns:
        A dictionary mapping section numbers to their content.
    """

    files = sorted([f for f in os.listdir(directory) if f.endswith('.txt')])
    files.insert(9,files[4])
    files.remove(files[4])

    sections = {}
    for i,file_name in enumerate(files):
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            sections[i+1] = file.read()
    return sections

def save_regulation_to_json(regulation: StudyRegulation, file_path: str) -> None:
    """Serialize a StudyRegulation object to JSON and save it to a file.
    
    Args:
        regulation: The StudyRegulation object to serialize.
        file_path: Path where the JSON file should be saved.
    """

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
    """Deserialize a StudyRegulation object from a JSON file.
    
    Args:
        file_path: Path to the JSON file containing the StudyRegulation.
        
    Returns:
        The deserialized StudyRegulation object.
    """

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
