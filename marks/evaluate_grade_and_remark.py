def evaluate_grade_and_remark(score):
    grades = {
        (0, 5): 'F',
        (5, 8): 'E',
        (8, 10): 'D',
        (10, 13): 'C',
        (13, 18): 'B',
        (18, 20): 'A',
    }
    remarks = {
        'A': 'Excellent',
        'B': 'Very Good',
        'C': 'Good',
        'D': 'Below Average',
        'E': 'Poor',
        'F': 'Very Poor'
    }

    if score == float(20):
        return ('A', 'Excellent')

    if score == float(10):
        return ('C', 'Average')

    for grade_range, letter_grade in grades.items():
        if grade_range[0] <= score < grade_range[1]:
            return (letter_grade, remarks[letter_grade])

    return ('N/A', 'N/A')
