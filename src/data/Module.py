from dataclasses import dataclass
import csv
import re
from _csv import Reader
from io import TextIOWrapper

@dataclass
class Module:
    """A class representing a module in the study regulation.

    This class handles the parsing and storage of module information from CSV files,
    including title, type, credit points, and various other module-specific details.
    """
    title: str
    short_title: str
    type: str
    credit_points: str
    presence_time: str
    self_time: str
    sws: str
    skills: str
    prerequ_part: str
    prerequ_mod: str
    deadline_try: str
    assign_study: str
    other_modules: str
    freq: str
    length: str
    lecturer: str
    proof_attendence: str
    proof_performance: str
    form: str
    exam_type: str

    def __init__(self, file: TextIOWrapper):
        """Initialize a Module instance from a CSV file.

        Args:
            file: A file object containing the module data in CSV format.
        """
        self.deadline_try = ""
        self.content_raw = self.get_csv_list(csv.reader(file))
        self.parse_content()
        if self.deadline_try == "":
            self.deadline_try = "Freiversuchsfrist: —"

        pattern = r'^(B-NLP-DS|[A-Z]+(?:-[A-Za-z0-9]+)*)([A-ZÄÖÜ].*)$'
        match = re.match(pattern, self.title)
        if match:
            self.short_title = match.group(1)
            self.title = match.group(2).strip()
        else:
            self.short_title = "n.a."
            self.title = "n.a."

    def __repr__(self) -> str:
        """Return a string representation of the module for LLM contexts."""
        return f"Modul: {self.title}; Abkürzung: {self.short_title}; Art: {self.type}; {self.credit_points}; {self.presence_time}; {self.self_time}; {self.skills}; {self.prerequ_part}; {self.prerequ_mod}; {self.deadline_try}; {self.assign_study}; {self.other_modules}; {self.freq}; {self.length}; {self.lecturer}; {self.proof_attendence}; {self.proof_performance}; {self.form}; {self.exam_type}"

    def __str__(self) -> str:
        """Return a formatted string representation of the module."""
        return f"""Module(
        Modul: {self.title};
        Abkürzung: {self.short_title};
        Art: {self.type};
        {self.credit_points};
        {self.presence_time};
        {self.self_time};
        {self.skills};
        {self.prerequ_part};
        {self.prerequ_mod};
        {self.deadline_try};
        {self.assign_study};
        {self.other_modules};
        {self.freq};
        {self.length};
        {self.lecturer};
        {self.proof_attendence};
        {self.proof_performance};
        {self.form};
        {self.exam_type}
        )"""

    def get_csv_list(self, rdr: Reader) -> list[list[str]]:
        """Convert CSV reader output to a list of lists of strings.

        Args:
            rdr: A CSV reader object containing the module data.

        Returns:
            A list of lists containing the parsed CSV data.
        """
        result_list = []
        for line in rdr:
            result_list.append(line)
        return result_list

    def parse_content(self):
        """Parse the raw CSV content and populate the module attributes."""
        i = 0
        self.title = self.content_raw[0][0].replace("\n", " ")
        self.type = self.content_raw[i][1].replace("\n", " ")
        i += 1
        self.credit_points = self.content_raw[i][0].replace("\n"," ").replace("CP", "Credit Points (CP)")
        self.presence_time = self.content_raw[i][1].replace("\n"," ").replace("SWS", "Semesterwochenstunden (SWS)")
        self.self_time = self.content_raw[i][2].replace("\n"," ")
        i += 1
        self.skills = self.content_raw[i][0].replace("\n"," ")
        i += 1
        self.prerequ_part = self.content_raw[i][0].replace("\n"," ")
        i += 1
        self.prerequ_mod = self.content_raw[i][0].replace("\n"," ")
        if "Basismodul" in self.type:
            i+= 1
            self.deadline_try = self.content_raw[i][0].replace("\n"," ")
        i += 1
        self.assign_study = " ".join(map(lambda x: x.replace("\n"," "), self.content_raw[i])).strip()
        i += 1
        self.other_modules = " ".join(map(lambda x: x.replace("\n"," "), self.content_raw[i])).strip()
        i += 1
        self.freq = " ".join(map(lambda x: x.replace("\n"," "), self.content_raw[i])).strip()
        i += 1
        self.length = " ".join(map(lambda x: x.replace("\n"," "), self.content_raw[i])).strip()
        i += 1
        self.lecturer = " ".join(map(lambda x: x.replace("\n"," "), self.content_raw[i][:2])).strip()
        i += 1
        self.proof_attendence = " ".join(map(lambda x: x.replace("\n"," "), self.content_raw[i][1:3])).strip()
        i += 1
        self.proof_performance = " ".join(map(lambda x: x.replace("\n"," "), self.content_raw[i][1:3])).strip()
        i += 1
        self.form = " ".join(map(lambda x: x.replace("\n"," "), self.content_raw[i][:2])).strip()
        i += 2
        self.exam_type = " ".join(map(lambda x: x.replace("\n"," "), self.content_raw[i][:2])).strip()
