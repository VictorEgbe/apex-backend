import string
from datetime import date
from random import randint


class StudentIDGenerator:
    def __init__(self, school_initials: str, query: list):
        self.school_initials = school_initials
        self.year_of_admission = str(date.today().year)
        self.letter_index = randint(0, 25)
        self.digit_index = randint(1, 999)
        self.query = query
        self.exhausted_index = 0

    def student_id_in_db(self, student_id):
        return student_id in self.query

    def generate_student_id(self):
        while True:
            letter = string.ascii_uppercase[self.letter_index % 26]
            number = str(self.digit_index).zfill(3)
            student_id = f"{self.school_initials}{str(self.year_of_admission)[-2:]}{letter}{number}"

            if self.student_id_in_db(student_id):
                self.exhausted_index += 1
                if self.exhausted_index == 20:
                    return "Ids are exhausted"
                continue
            else:
                break

        return student_id
