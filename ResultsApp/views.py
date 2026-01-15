from django.shortcuts import render , redirect
from django.contrib.auth import authenticate , login
from django.contrib import messages
from .models import Subject
from .models import SubjectCombination, Subject, Student, Notice, Result, Department, TeacherProfile 
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Class
from .forms import DepartmentForm
from django.utils import timezone
from django.contrib import messages
from .models import Student, Class  # Class model
from .models import TeacherProfile, Department
from django import forms
from django.db import IntegrityError
from django.contrib.auth.models import User
from .forms import TeacherRegistrationForm
from .models import Department, TeacherProfile, Subject
from .forms import DepartmentForm
from datetime import datetime
import csv
import io
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from django.contrib.auth.hashers import make_password
from reportlab.lib import colors
from django.http import JsonResponse
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.urls import reverse_lazy

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'

# Create your views here.
def index(request):
    # Get all notices, latest first
    notices = Notice.objects.all().order_by('-posting_date')
    return render(request, 'index.html', {'notices': notices})
    
def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    error = None
    user = None   # ✅ define user first

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            error = "Invalid credentials or not authorised."

    return render(request, 'admin_login.html', {'error': error})

def admin_dashboard(request):
    # Counts
    total_students = Student.objects.count()
    total_teachers = TeacherProfile.objects.count()
    total_classes = Class.objects.count()
    total_subjects = Subject.objects.count()
    total_departments = Department.objects.count()
    total_notices = Notice.objects.count()

    # Results logic
    total_results = Result.objects.count()
    expected_results = total_students * total_subjects

    if expected_results > 0:
        results_percentage = round((total_results / expected_results) * 100, 1)
    else:
        results_percentage = 0

    # ✅ Ensure cls_id exists
    first_class = Class.objects.first()  # Get the first class
    cls_id = first_class.id if first_class else None

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_classes': total_classes,
        'total_subjects': total_subjects,
        'total_departments': total_departments,
        'total_notices': total_notices,
        'total_results': total_results,
        'results_percentage': results_percentage,
        'cls_id': cls_id,  # Pass it to template
    }

    return render(request, "admin_dashboard.html", context)

def admin_logout(request):
    logout(request)
    return redirect('admin_login')

@login_required
def create_class(request):
    # Determine dashboard URL based on user role
    if request.user.is_staff:
        dashboard_url = 'admin_dashboard'
    else:
        dashboard_url = 'teacher_dashboard'

    if request.method == 'POST':
        class_name = request.POST.get('class_name')
        numeric_name = request.POST.get('numeric_name')
        section = request.POST.get('section')

        if not class_name or not numeric_name or not section:
            messages.error(request, 'All fields are required')
            return redirect('create_class')

        try:
            Class.objects.create(
                class_name=class_name,
                numeric_name=numeric_name,
                section=section
            )
            messages.success(request, 'Class successfully created')
        except Exception as e:
            print("ERROR:", e)  # shows real error in terminal
            messages.error(request, 'Something went wrong')

        return redirect('create_class')

    # Pass the dashboard URL to the template
    return render(request, 'create_class.html', {
        'user_dashboard_url': dashboard_url
    })

@login_required
def manage_classes(request):
    classes = Class.objects.all().order_by('numeric_name', 'class_name', 'section')
    return render(request, 'manage_classes.html', {'classes': classes})

def edit_class(request, class_id):
    cls = get_object_or_404(Class, id=class_id)
    if request.method == 'POST':
        cls.class_name = request.POST.get('class_name')
        cls.numeric_name = request.POST.get('numeric_name')
        cls.section = request.POST.get('section')
        cls.save()
        messages.success(request, 'Class updated successfully')
        return redirect('manage_classes')
    return render(request, 'edit_class.html', {'cls': cls})

def delete_class(request, class_id):
    cls = get_object_or_404(Class, id=class_id)
    cls.delete()
    messages.success(request, 'Class deleted successfully')
    return redirect('manage_classes')

@login_required
def create_subject(request):
    departments = Department.objects.all()

    # Set the dashboard URL depending on user type
    if request.user.is_staff:
        user_dashboard_url = 'admin_dashboard'
    else:
        user_dashboard_url = 'teacher_dashboard'

    if request.method == "POST":
        subject_name = request.POST.get('subject_name')
        subject_code = request.POST.get('subject_code')
        department_id = request.POST.get('department_id')

        try:
            department = Department.objects.get(id=department_id)
            Subject.objects.create(
                subject_name=subject_name,
                subject_code=subject_code,
                department=department
            )
            messages.success(request, "Subject created successfully")
        except Exception as e:
            print("ERROR:", e)
            messages.error(request, "Something went wrong")

        return redirect('create_subject')

    context = {
        'departments': departments,
        'user_dashboard_url': user_dashboard_url
    }
    return render(request, 'create_subject.html', context)


@login_required
def manage_subjects(request, class_id):
    subjects = Subject.objects.select_related('department').all().order_by('subject_name', 'subject_code')
    return render(request, 'manage_subjects.html', {'subjects': subjects})

def edit_subject(request, subject_id):
    cls = get_object_or_404(Subject, id= subject_id)
    if request.method == 'POST':
        cls.subject_name = request.POST.get('subject_name')
        cls.subject_code = request.POST.get('subject_code')
        cls.save()
        messages.success(request, 'Subject updated successfully')
        return redirect('manage_subjects')
    return render(request, 'edit_subject.html', {'cls': cls})

def delete_subject(request, subject_id):
    cls = get_object_or_404(Subject, id=subject_id)
    cls.delete()
    messages.success(request, 'Subject deleted successfully')
    return redirect('manage_subjects')

def add_subject_combination(request):
    classes = Class.objects.all()
    subjects = Subject.objects.all()

    if request.method == "POST":
        # Get IDs from the POST request
        student_class_id = request.POST.get('student_class')
        subject_id = request.POST.get('subject')

        # Fetch instances from the database
        student_class = get_object_or_404(Class, id=student_class_id)
        subject = get_object_or_404(Subject, id=subject_id)

        # Create a valid SubjectCombination
        SubjectCombination.objects.create(
            student_class=student_class,
            subject=subject
        )

        messages.success(request, "Subject combination successfully created")
        return redirect('add_subject_combination')

    context = {
        'classes': classes,
        'subjects': subjects
    }
    return render(request, 'add_subject_combination.html', context)

@login_required
def manage_subject_combination(request):
    combinations = SubjectCombination.objects.all()
    context = {
        'combinations': combinations
    }
    return render(request, 'manage_subject_combination.html',context)
def edit_subject_combination(request, subject_id):  # <-- accept the ID
    combination = get_object_or_404(SubjectCombination, id=subject_id)
    classes = Class.objects.all()
    subjects = Subject.objects.all()

    if request.method == "POST":
        student_class_id = request.POST.get('student_class')
        subject_id_post = request.POST.get('subject')  # POST data
        student_class = get_object_or_404(Class, id=student_class_id)
        subject = get_object_or_404(Subject, id=subject_id_post)

        combination.student_class = student_class
        combination.subject = subject
        combination.save()

        messages.success(request, "Subject combination updated successfully")
        return redirect('manage_subject_combination')

    context = {
        'combination': combination,
        'classes': classes,
        'subjects': subjects
    }
    return render(request, 'edit_subject_combination.html', context)

def delete_subject_combination(request, subject_id):  # <-- accept the argument
    combination = get_object_or_404(SubjectCombination, id=subject_id)

    if request.method == "POST":
        combination.delete()
        messages.success(request, "Subject combination deleted successfully")
        return redirect('manage_subject_combination')  # make sure this URL name exists
    
def add_student(request):
    classes = Class.objects.all()

    if request.method == "POST":
        student_name = request.POST.get("student_name")
        student_class_id = request.POST.get("student_class")
        exam_no = request.POST.get("exam_no")
        phone_no = request.POST.get("phone_no")
        gender = request.POST.get("gender")
        dob = request.POST.get("dob")
        address = request.POST.get("address")

        if not all([student_name, student_class_id, exam_no, phone_no, gender, dob, address]):
            messages.error(request, "All fields are required")
            return redirect("add_student")

        try:
            student_class = Class.objects.get(id=student_class_id)

            Student.objects.create(
                student_name=student_name,
                student_class=student_class,
                exam_no=exam_no,     # adjust if needed
                phone_no=phone_no,  # required if model needs it
                gender=gender,
                dob=dob,
                address=address,
            )

            messages.success(request, "Student successfully created")
            return redirect("add_student")

        except Exception as e:
            print("ERROR 👉", e)
            messages.error(request, str(e))
            return redirect("add_student")

    return render(request, "add_student.html", {"classes": classes})

@login_required
def manage_students(request):
    classes = Student.objects.all().order_by('student_name', 'student_class','exam_no','phone_no','gender','dob','address')
    return render(request, 'manage_students.html', {'classes': classes})
@login_required
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    classes = Class.objects.all()  # all classes for the dropdown

    if request.method == 'POST':
        # Fetch POST data
        student_name = request.POST.get('student_name')
        exam_no = request.POST.get('exam_no')
        phone_no = request.POST.get('phone_no')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        address = request.POST.get('address')
        class_id = request.POST.get('student_class')

        # Convert class_id to Class instance
        student_class_instance = get_object_or_404(Class, id=class_id)

        # Update student fields
        student.student_name = student_name
        student.student_class = student_class_instance  # assign instance
        student.exam_no = exam_no
        student.phone_no = phone_no
        student.gender = gender
        student.dob = dob
        student.address = address

        student.save()
        messages.success(request, 'Student updated successfully')
        return redirect('manage_students')

    return render(request, 'edit_student.html', {
        'student': student,
        'classes': classes,
    })


def delete_student(request, student_id):
    cls = get_object_or_404(Student, id=student_id)
    cls.delete()
    messages.success(request, 'Student deleted successfully')
    return redirect('manage_students')

def add_notice(request):
    if request.method == "POST":
        title = request.POST.get('title')
        details = request.POST.get('details')

        if not title:
            messages.error(request, "Title is required")
            return redirect("add_notice")

        Notice.objects.create(title=title, details=details)
        messages.success(request, "Notice successfully posted")
        return redirect("add_notice")

    return render(request, "ResultsApp/add_notice.html")

@login_required
def manage_notice(request):
    notices = Notice.objects.all()

    # Check if 'delete' parameter is in GET
    notice_id = request.GET.get('delete')
    if notice_id:
        notice = get_object_or_404(Notice, id=notice_id)
        notice.delete()
        messages.success(request, 'Notice deleted successfully')
        return redirect('manage_notice')

    return render(request, 'ResultsApp/manage_notice.html', {'notices': notices})

def edit_notice(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)

    if request.method == "POST":
        title = request.POST.get('title')
        details = request.POST.get('details')

        if not title:
            messages.error(request, "Title is required")
            return redirect('edit_notice', notice_id=notice_id)

        notice.title = title
        notice.details = details
        notice.save()

        messages.success(request, "Notice updated successfully")
        return redirect('manage_notice')

    return render(request, "ResultsApp/edit_notice.html", {"notice": notice})

@login_required
def add_result(request):
    user = request.user
    is_admin = user.is_superuser

    if not is_admin:
        teacher = user.teacherprofile
        department = teacher.department

        # Teacher: classes and subjects restricted to department
        classes = Class.objects.filter(
            subjectcombination__subject__department=department
        ).distinct()
        subjects = Subject.objects.filter(department=department)
    else:
        # Admin: all classes and subjects
        classes = Class.objects.all()
        subjects = Subject.objects.all()

    years = range(2020, 2031)
    current_year = timezone.now().year

    if request.method == "POST":
        class_id = request.POST.get("class")
        subject_id = request.POST.get("subject")
        term = request.POST.get("term")
        year = request.POST.get("year")

        # Validate teacher selections
        if not is_admin:
            if not Class.objects.filter(id=class_id, subjectcombination__subject__department=department).exists():
                messages.error(request, "Invalid class selection for your department.")
            elif not Subject.objects.filter(id=subject_id, department=department).exists():
                messages.error(request, "Invalid subject selection for your department.")
            else:
                return redirect('enter_marks', class_id=class_id, subject_id=subject_id, term=term, year=year)
        else:
            return redirect('enter_marks', class_id=class_id, subject_id=subject_id, term=term, year=year)

    return render(request, "ResultsApp/add_result.html", {
        "classes": classes,
        "subjects": subjects,
        "years": years,
        "current_year": current_year,
        "is_admin": is_admin,
    })

from django.http import JsonResponse
def get_students_subjects(request):
    class_id = request.GET.get('class_id')

    if class_id:
        # Get students in this class
        students = Student.objects.filter(student_class_id=class_id).values('id', 'student_name', 'exam_no')

        # Get subjects in this class
        subject_combinations = SubjectCombination.objects.filter(
            student_class__id=class_id,
            status=1
        ).select_related('subject')

        subjects = [
            {
                'id': sc.subject.id,
                'name': sc.subject.subject_name
            }
            for sc in subject_combinations
        ]

        return JsonResponse({
            'students': list(students),
            'subjects': subjects
        })

    return JsonResponse({'students': [], 'subjects': []})

@login_required
def manage_results(request, class_id=None):
    user = request.user

    # Check if the user is a teacher
    try:
        teacher = user.teacherprofile
        is_teacher = True
    except TeacherProfile.DoesNotExist:
        teacher = None
        is_teacher = False

    # Classes available in the filter
    classes = Class.objects.all()  # admin sees all classes
    if is_teacher:
        # Optionally, limit to classes where teacher has subjects
        # classes = Class.objects.filter(subjectcombination__subject__department=teacher.department).distinct()
        pass

    class_instance = None
    if class_id:
        class_instance = get_object_or_404(Class, id=class_id)

    context = {
        'classes': classes,
        'class_instance': class_instance,
        'is_teacher': is_teacher,
        'now': timezone.now(),
    }
    return render(request, 'ResultsApp/manage_results.html', context)

def get_students_by_class(request):
    class_id = request.GET.get("class_id")
    students = []

    if class_id:
        students_qs = Student.objects.filter(student_class_id=class_id)
        students = [
            {"id": s.id, "name": s.student_name, "exam_no": s.exam_no}
            for s in students_qs
        ]

    return JsonResponse({"students": students})

from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

# Fetch subjects by class (AJAX)
@login_required
def get_subjects_by_class(request):
    class_id = request.GET.get('class_id')
    user = request.user

    subjects = Subject.objects.none()
    if not class_id:
        return JsonResponse({'subjects': []})

    class_instance = get_object_or_404(Class, id=class_id)

    # Get all subjects assigned to this class
    subjects_in_class = Subject.objects.filter(
        subjectcombination__student_class=class_instance
    ).distinct()

    try:
        teacher = user.teacherprofile
        # Filter to teacher's department
        dept_subjects = subjects_in_class.filter(department=teacher.department)
        if dept_subjects.exists():
            subjects = dept_subjects
        else:
            # If none in teacher's department, show all subjects for the class
            subjects = subjects_in_class
    except TeacherProfile.DoesNotExist:
        # Admin sees all
        subjects = subjects_in_class

    subjects_list = [
        {'id': s.id, 'name': s.subject_name, 'code': s.subject_code} for s in subjects
    ]
    return JsonResponse({'subjects': subjects_list})

# Update results (AJAX POST)
@csrf_exempt
def update_results(request):
    if request.method == "POST":
        class_id = request.POST.get("class_id")
        subject_id = request.POST.get("subject_id")
        test_type = request.POST.get("test_type")
        term = request.POST.get("term")
        year = request.POST.get("year")

        for key, value in request.POST.items():
            if key.startswith("marks_") and value != "":
                student_id = key.split("_")[1]

                Result.objects.update_or_create(
                    student_id=student_id,
                    subject_id=subject_id,
                    test_type=test_type,
                    term=term,
                    year=year,
                    defaults={
                        "marks": value,
                        "student_class_id": class_id,
                        "updation_date": timezone.now(),
                    }
                )

        return JsonResponse({"status": "success"})
    
@login_required
def delete_results(request):
        if request.method == "POST":
         class_id = request.POST.get("class_id")
         subject_id = request.POST.get("subject_id")
         test_type = request.POST.get("test_type")
         term = request.POST.get("term")
         year = request.POST.get("year")

        Result.objects.filter(
            student_class_id=class_id,
            subject_id=subject_id,
            test_type=test_type,
            term=term,
            year=year
        ).delete()

        messages.success(request, "Results deleted successfully")
        return JsonResponse({"status": "success"})

@login_required
def view_results(request):
    classes = Class.objects.all()
    return render(request, "ResultsApp/view_results.html", {"classes": classes})

@login_required
def download_results_pdf(request):
    class_id = request.GET.get('class_id')
    subject_id = request.GET.get('subject_id')
    test_type = request.GET.get('test_type')
    term = request.GET.get('term')
    year = request.GET.get('year')

    if not all([class_id, subject_id, test_type, term, year]):
        return HttpResponse("Missing required parameters!", status=400)

    # Fetch class, subject, students and results
    my_class = get_object_or_404(Class, id=class_id)
    subject = get_object_or_404(Subject, id=subject_id)
    students = Student.objects.filter(student_class=my_class).order_by('student_name')

    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Results_{my_class}_{subject}_{term}_{year}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title = Paragraph(f"Class: {my_class.class_name} {my_class.numeric_name} {my_class.section} <br/>"
                      f"Subject: {subject.subject_name} ({subject.subject_code}) <br/>"
                      f"Test: {test_type} | Term: {term} | Year: {year}", styles['Title'])
    elements.append(title)
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # Table data
    data = [['S.No', 'Student Name', 'Exam Number', 'Gender', 'Marks']]
    for idx, student in enumerate(students, start=1):
        result = Result.objects.filter(
            student=student,
            subject=subject,
            test_type=test_type,
            term=term,
            year=year
        ).first()
        marks = result.marks if result else ''
        data.append([idx, student.student_name, student.exam_no, student.gender, marks])

    # Table styling
    table = Table(data, colWidths=[40, 150, 100, 60, 60])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))

    elements.append(table)
    doc.build(elements)
    return response


@login_required
def get_results(request):
    class_id = request.GET.get('class_id')
    subject_id = request.GET.get('subject_id')
    test_type = request.GET.get('test_type')
    term = request.GET.get('term')
    year = request.GET.get('year')

    if not all([class_id, subject_id, test_type, term, year]):
        return JsonResponse({'results': []})

    class_instance = get_object_or_404(Class, id=class_id)
    subject = get_object_or_404(Subject, id=subject_id)

    students = Student.objects.filter(student_class=class_instance)

    # If teacher, check they can only see their department's subjects
    user = request.user
    try:
        teacher = user.teacherprofile
        if subject.department != teacher.department:
            return JsonResponse({'results': []})
    except TeacherProfile.DoesNotExist:
        pass

    results = Result.objects.filter(
        student__in=students,
        subject=subject,
        test_type=test_type,
        term=term,
        year=year
    )

    results_list = [
        {
            'student_id': r.student.id,
            'student_name': r.student.student_name,
            'exam_no': r.student.exam_no,
            'marks': r.marks
        }
        for r in results
    ]
    return JsonResponse({'results': results_list})

from .forms import TeacherRegistrationForm

def teacher_register(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Teacher registered successfully!")
                return redirect('teacher_login')  # redirect to login page
            except IntegrityError:
                messages.error(request, "A teacher with this email already exists.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TeacherRegistrationForm()

    return render(request, 'ResultsApp/teacher_register.html', {'form': form})



def teacher_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('teacher_dashboard')
        else:
            messages.error(request, "Invalid email or password")

    return render(request, 'ResultsApp/teacher_login.html')

@login_required
def enter_result(request):
    teacher = getattr(request.user, 'teacherprofile', None)

    if not teacher:
        messages.error(request, "You do not have a teacher profile.")
        return redirect('teacher_login')

    department = teacher.department
    students = Student.objects.filter(student_class__department=department)
    subjects = Subject.objects.all()  

    context = {
        'teacher': teacher,
        'department': department,
        'students': students,
        'subjects': subjects,
    }

    return render(request, 'ResultsApp/enter_result.html', context)


# Add department
@login_required
def add_department(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Department added successfully")
            return redirect('manage_departments')
    else:
        form = DepartmentForm()

    return render(request, 'ResultsApp/add_department.html', {'form': form})

@login_required
def manage_departments(request):
    departments = Department.objects.all()

    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_departments')
    else:
        form = DepartmentForm()

    context = {
        'form': form,
        'departments': departments
    }
    return render(request, 'manage_departments.html', context)


# Edit department
def edit_department(request, department_id):
    dept = get_object_or_404(Department, id=department_id)
    if request.method == "POST":
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            form.save()
            messages.success(request, f"Department '{dept.department_name}' updated successfully.")
            return redirect('manage_departments')
    else:
        form = DepartmentForm(instance=dept)
    return render(request, 'edit_department.html', {'form': form})

# Delete department
def delete_department(request, department_id):
    dept = get_object_or_404(Department, id=department_id)
    
    # Optional: set department to null for teachers and subjects before deletion
    TeacherProfile.objects.filter(department=dept).update(department=None)
    Subject.objects.filter(department=dept).update(department=None)

    dept.delete()
    messages.success(request, f"Department '{dept.department_name}' deleted successfully.")
    return redirect('manage_departments')

def notice_detail(request, notice_id):
    # Get the notice object or show 404 if it doesn't exist
    notice = get_object_or_404(Notice, id=notice_id)
    return render(request, 'notice_detail.html', {'notice': notice})

@login_required
def teacher_dashboard(request):
    teacher = request.user.teacherprofile

    subjects = Subject.objects.filter(department=teacher.department)
    subject_combinations = SubjectCombination.objects.filter(subject__in=subjects).distinct()
    classes = Class.objects.filter(subjectcombination__in=subject_combinations).distinct()
    students_count = Student.objects.filter(student_class__in=classes).count()

    # Use first class id for the link
    cls_id = classes.first().id if classes.exists() else None

    context = {
        'teacher': teacher,
        'classes': classes,
        'classes_count': classes.count(),
        'students_count': students_count,
        'subjects_count': subjects.count(),
        'cls_id': cls_id,  # pass cls_id to template
    }

    return render(request, 'teacher/teacher_dashboard.html', context)

@login_required
def teacher_logout(request):
    logout(request)
    return redirect('home')

@login_required
def add_teacher(request):
    if request.method == "POST":
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Teacher added successfully")
            return redirect('manage_teachers')
        else:
            messages.error(request, "Please fix the errors below")
    else:
        form = TeacherRegistrationForm()
    return render(request, 'admin/add_teacher.html', {'form': form})

# Manage Teachers View
@login_required
def manage_teachers(request):
    teachers = TeacherProfile.objects.select_related('user', 'department').all()
    return render(request, 'admin/manage_teachers.html', {'teachers': teachers})

def edit_teacher(request, teacher_id):
    teacher = get_object_or_404(TeacherProfile, id=teacher_id)

    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST, instance=teacher)
        if form.is_valid():
            # Update password if entered
            password = form.cleaned_data.get('password')
            if password:
                teacher.user.set_password(password)
                teacher.user.save()  # important!

            form.save()
            messages.success(request, "Teacher details updated successfully!")
            return redirect('edit_teacher', teacher_id=teacher.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TeacherRegistrationForm(instance=teacher)

    return render(request, 'edit_teacher.html', {'form': form, 'teacher': teacher})


@login_required
def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(TeacherProfile, id=teacher_id)
    teacher.user.delete()  # deletes the linked User too
    teacher.delete()
    messages.success(request, "Teacher deleted successfully")
    return redirect('manage_teachers')

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        phone = request.POST.get('phone')

        try:
            user = User.objects.get(username=username)
            profile = TeacherProfile.objects.get(user=user, phone_no=phone)

            # Store user ID in session (secure)
            request.session['reset_user_id'] = user.id

            # Redirect directly to reset password page
            return redirect('reset_password')

        except User.DoesNotExist:
            messages.error(request, "User not found")
        except TeacherProfile.DoesNotExist:
            messages.error(request, "Verification failed")

    return render(request, 'forgot_password.html')


def reset_password(request):
    user_id = request.session.get('reset_user_id')

    if not user_id:
        messages.error(request, "Access denied")
        return redirect('forgot_password')

    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
        else:
            user.password = make_password(password1)
            user.save()
            del request.session['reset_user_id']
            messages.success(request, "Password reset successful")
            return redirect('teacher_login')

    return render(request, 'reset_password.html')

@login_required
def teacher_logout(request):
    logout(request)
    return redirect('index') 









