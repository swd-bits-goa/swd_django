from datetime import datetime, timedelta
import random
import csv


def conv_to_array(csv_file):
    """
    Converts csv file to an array object with each row as dictionary element.
    """
    total_student_data = []

    reader = csv.DictReader(csvfile)
    for student in reader:
        if student is not None:
            total_student_data.append(dict(student))

    return total_student_data


def gen_random_datetime(min_year=1900, max_year=datetime.now().year):
    """
    Generates random datetime object
    """
    start = datetime(min_year, 1, 1, 00, 00, 00)
    years = max_year - min_year + 1
    end = start + timedelta(days=365 * years)
    result = start + (end - start) * random.random()
    return result
