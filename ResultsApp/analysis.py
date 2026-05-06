from .models import Student, Result, Class, GradingSystem
from collections import defaultdict
from django.db.models import Avg
# ResultsApp/analysis.py
from django.db.models import Count, Q
from .models import (
    Class, Student, Result, GradingSystem
)

FAIL_GRADE = 'F'
PASS_GRADES_JUNIOR = ['1', '2', '3', '4']

def analyze_junior_results(term, test_type, year, student_class):
    """
    Analyze Junior results for a given class, term, and test type.
    Returns a list of dictionaries per subject with ECZ-style summary stats.
    """
    subjects = Result.objects.filter(
        term=term,
        test_type=test_type,
        year=year,
        student__student_class=student_class
    ).values_list('subject', flat=True).distinct()

    try:
        grading_system = GradingSystem.objects.get(class_level='JUNIOR')
    except GradingSystem.DoesNotExist:
        return []

    grades = grading_system.grades.all().order_by('-min_mark')  # Highest mark first

    summary_rows = []

    students = Student.objects.filter(student_class=student_class)

    for subject in subjects:
        results = Result.objects.filter(
            term=term,
            test_type=test_type,
            year=year,
            subject=subject,
            student__student_class=student_class
        )

        # Initialize stats
        stats = {'Male': defaultdict(int), 'Female': defaultdict(int)}

        # Calculate average marks per student
        grouped = results.values('student_id', 'student__gender').annotate(avg_mark=Avg('marks'))

        for r in grouped:
            gender = r['student__gender']
            avg_mark = r['avg_mark']

            # Determine grade
            grade_obj = grades.filter(min_mark__lte=avg_mark).order_by('-min_mark').first()
            if grade_obj:
                grade = grade_obj.grade
            else:
                grade = FAIL_GRADE

            stats[gender]['sat'] += 1

            if grade in PASS_GRADES_JUNIOR:
                stats[gender][f'grade_{grade}'] += 1
            else:
                stats[gender]['failed'] += 1

        # Calculate enrolled, absent, passed, pass %
        for gender in ['Male', 'Female']:
            enrolled = students.filter(gender=gender[0]).count()  # 'M' or 'F'
            sat = stats[gender]['sat']
            passed = sum(stats[gender][f'grade_{g}'] for g in PASS_GRADES_JUNIOR)
            failed = stats[gender]['failed']

            stats[gender]['enrolled'] = enrolled
            stats[gender]['absent'] = enrolled - sat
            stats[gender]['passed'] = passed
            stats[gender]['pass_pct'] = round((passed / sat * 100) if sat else 0, 2)
            stats[gender]['failed'] = failed

        # Total pass %
        total_sat = stats['Male']['sat'] + stats['Female']['sat']
        total_pass = stats['Male']['passed'] + stats['Female']['passed']
        total_pass_pct = round((total_pass / total_sat * 100) if total_sat else 0, 2)

        summary_rows.append({
            'subject': subject,
            'male': stats['Male'],
            'female': stats['Female'],
            'grades': [g.grade for g in grades],  # To build columns in template
            'pass_pct_total': total_pass_pct
        })

    return summary_rows

PASS_GRADES_SENIOR_1_6 = ['1','2','3','4','5','6']
PASS_GRADES_SENIOR_1_8 = ['1','2','3','4','5','6','7','8']
FAIL_GRADE = 'F'

def analyze_senior_results(term, test_type, year, student_class):
    # Get subjects with results
    subjects = Result.objects.filter(
        term=term,
        test_type=test_type,
        year=year,
        student__student_class=student_class
    ).values_list('subject', flat=True).distinct()

    try:
        grading_system = GradingSystem.objects.get(class_level='SENIOR')
        grades = grading_system.grades.all().order_by('-min_mark')
    except GradingSystem.DoesNotExist:
        grades = []

    students = Student.objects.filter(student_class=student_class)
    summary_rows = []

    for subject in subjects:
        results = Result.objects.filter(
            term=term,
            test_type=test_type,
            year=year,
            subject=subject,
            student__student_class=student_class
        )

        stats = {'Male': defaultdict(int), 'Female': defaultdict(int)}
        grouped = results.values('student_id', 'student__gender').annotate(avg_mark=Avg('marks'))

        for r in grouped:
            gender = r['student__gender']
            avg_mark = r['avg_mark']

            grade_obj = grades.filter(min_mark__lte=avg_mark).order_by('-min_mark').first() if grades else None
            grade = grade_obj.grade if grade_obj else FAIL_GRADE

            stats[gender]['sat'] += 1
            stats[gender][f'grade_{grade}'] += 1
            if grade not in [g.grade for g in grades] or grade == FAIL_GRADE:
                stats[gender]['failed'] += 1

        for gender in ['Male','Female']:
            enrolled = students.filter(gender=gender[0]).count()
            sat = stats[gender]['sat']
            passed_1_6 = sum(stats[gender][f'grade_{g}'] for g in PASS_GRADES_SENIOR_1_6)
            passed_1_8 = sum(stats[gender][f'grade_{g}'] for g in PASS_GRADES_SENIOR_1_8)
            failed = stats[gender]['failed']

            stats[gender]['enrolled'] = enrolled
            stats[gender]['absent'] = enrolled - sat
            stats[gender]['passed_1_6'] = passed_1_6
            stats[gender]['passed_1_8'] = passed_1_8
            stats[gender]['pass_pct_1_6'] = round((passed_1_6/sat*100) if sat else 0,2)
            stats[gender]['pass_pct_1_8'] = round((passed_1_8/sat*100) if sat else 0,2)
            stats[gender]['failed'] = failed

        summary_rows.append({
            'subject': subject,
            'male': stats['Male'],
            'female': stats['Female'],
            'grades': [g.grade for g in grades],
        })

    return summary_rows