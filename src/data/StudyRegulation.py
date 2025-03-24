from dataclasses import dataclass
from typing import Optional
import re

@dataclass
class SubPoint:
    number: str
    content: str

@dataclass
class Point:
    number: str
    content: str
    subpoints: list[SubPoint]

@dataclass
class Paragraph:
    number: str
    title: Optional[str]
    content: str
    points: list[Point]

@dataclass
class Section:
    number: str
    title: str
    paragraphs: list[Paragraph]

@dataclass
class StudyRegulation:
    sections: list[Section]

def parse_subpoints(text: str) -> list[SubPoint]:
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

def parse_points(text: str) -> list[Point]:
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

def parse_paragraphs(text: str) -> list[Paragraph]:
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


def parse_section_without_subpoints(text: str) -> Section:
    section_match = re.match(r'Abschnitt ([IVXLCDM]+):\s*(.*?)(?=\n\s*§)', text, re.DOTALL)
    if not section_match:
        raise ValueError("Invalid section format")

    number, title = section_match.groups()
    paragraphs = parse_paragraphs_without_subpoints(text)

    return Section(number=number, title=title.strip(), paragraphs=paragraphs)

def parse_paragraphs_without_subpoints(text: str) -> list[Paragraph]:
    para_pattern = r'(?:^|\n\n|\n(?=§))§\s*(\d+)\s+([^(\n]+(?:\([^)]+\)[^(\n]+)*?)(?:\((RO:?\s*(?:§\s*)?\d+)\))?\s*\n+(.*?)(?=(?:\n\n|\n(?=§))§\s*\d+(?:\s+(?!Abs))|$)'
    paragraphs = []

    for match in re.finditer(para_pattern, text, re.DOTALL):
        number, title_text, ro_ref, content = match.groups()

        title = title_text.strip()
        # if ro_ref:
        #     title = f"{title} ({ro_ref})"

        points = parse_points_without_subpoints(content)

        # If points were found, remove their text from the content
        if points:
            content = re.sub(r'\(\d+\).*?(?=\(\d+\)|$)', '', content, flags=re.DOTALL).strip()

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


def parse_points_without_subpoints(text: str) -> list[Point]:
    point_pattern = r'\((\d+)\)\s*(.*?)(?=(?:\(\d+\)|$))'
    points = []
    for match in re.finditer(point_pattern, text, re.DOTALL):
        number, content = match.groups()

        points.append(Point(
            number=number,
            content=content.strip(),
            subpoints=[]  # No subpoints
        ))
    return points
