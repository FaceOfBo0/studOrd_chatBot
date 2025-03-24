from dataclasses import dataclass
import csv
from io import TextIOWrapper

@dataclass
class Module:
    title: str
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
        self.deadline_try = ""
        self.reader = csv.reader(file)
        self.content_raw = self.get_csv_list()
        self.parse_content()
        if self.deadline_try == "":
            self.deadline_try = "Freiversuchsfrist: —"

    def __repr__(self) -> str:
        return f"{self.title}; {self.type}; {self.credit_points}; {self.presence_time}; {self.self_time}; {self.skills}; {self.prerequ_part}; {self.prerequ_mod}; {self.deadline_try}; {self.assign_study}; {self.other_modules};"

    def __str__(self) -> str:
        return f"""Module(
        {self.title};
        {self.type};
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

    def __del__(self):
        pass

    def get_csv_list(self) -> list[list[str]]:
        result_list = []
        for line in self.reader:
            result_list.append(line)
        return result_list

    def transform_title(self, title_raw: str) -> str:
        return title_raw

    def parse_content(self):
        i = 0
        self.title = "Modul: " + self.transform_title(self.content_raw[0][0].replace("\n", " "))
        self.type = "Art: " + self.content_raw[i][1].replace("\n", " ")
        i += 1
        self.credit_points = self.content_raw[i][0].replace("\n"," ").replace("CP", "Credit Points")
        self.presence_time = self.content_raw[i][1].replace("\n"," ")
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

def parse_modules(mods_dir: str) -> list[Module]:
    return []
