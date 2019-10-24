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
