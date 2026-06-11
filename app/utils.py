def calculate_percentage(marks_obtained: float, total_marks: float) -> float:
    return (marks_obtained / total_marks) * 100

def get_grade_letter(percentage: float) -> str:
    if percentage >= 90:
        return "A"
    elif percentage >= 80:
        return "B"
    elif percentage >= 70:
        return "C"
    elif percentage >= 60:
        return "D"
    else:
        return "F"