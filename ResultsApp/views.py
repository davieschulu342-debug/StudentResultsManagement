from django.shortcuts import render , redirect
from django.contrib.auth import authenticate , login
from django.contrib import messages
from .models import SubjectCombination, Subject, Student, Notice, Result, Department, TeacherProfile
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import TeacherMaterial, StudentMaterial
from django.db.models import Count
from .forms import DepartmentForm
from reportlab.lib.units import cm
import json
from django.http import Http404
from django.utils import timezone
from .models import Student, Class  # Class model
from .models import TeacherProfile, Department
from django import forms
from .models import Message, Notification
from .forms import MessageForm
from django.contrib.auth import get_user_model
from django.conf import settings
import os
from .forms import NoticeForm
from ResultsApp.utils import render_to_pdf
from ResultsApp.constants import TERM_REVERSE_MAP, TEST_REVERSE_MAP
from ResultsApp.models import GradingSystem, Grade
from django.template.loader import render_to_string
import pdfkit 
from django.db.models import F, Value
from django.db.models.functions import Concat
from openpyxl import Workbook
from django.db import IntegrityError
from django.contrib.auth.models import User
from .forms import TeacherRegistrationForm
from .models import Department, TeacherProfile, Subject
from .forms import StudentForm
from datetime import datetime
import csv
from .forms import TeacherRegistrationForm
import io
import os
import weasyprint
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from django.conf import settings
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.platypus import Image as RLImage
from weasyprint import HTML
import pandas as pd
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import paragraph, Image
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from django.contrib.auth.hashers import make_password
from reportlab.lib import colors
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from io import BytesIO
from ResultsApp.models import Result
from django.db.models import CharField
from django.db.models.functions import Cast
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.urls import reverse_lazy
from django.conf import settings
import os
from urllib.parse import urlparse

def index(request):
    # Get notices or any other context as needed
    notices = Notice.objects.all()[:5]  # Example if you have a Notice model
    context = {
        'show_navbar': True,
        'notices': notices
    }
    return render(request, 'index.html', context)




def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access them
    """
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        return uri

    if not os.path.isfile(path):
        raise Exception(f"Media URI must start with {settings.STATIC_URL} or {settings.MEDIA_URL}")

    return path

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
    # Log out any currently logged-in user
    if request.user.is_authenticated:
        logout(request)

    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:  # Only allow superusers
            login(request, user)
            return redirect('admin_dashboard')
        else:
            error = "Invalid credentials or not authorised."

    return render(request, 'admin_login.html', {'error': error})

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render

from .decorators import admin_required
from .models import (
    Student, TeacherProfile, Class,
    Subject, Department, Notice, Result
)

@login_required
@admin_required
def admin_dashboard(request):

    total_students = Student.objects.count()
    total_teachers = TeacherProfile.objects.count()
    total_subjects = Subject.objects.count()
    total_classes = Class.objects.count()
    total_departments = Department.objects.count()
    total_notices = Notice.objects.count()
    total_results = Result.objects.count()

    expected_results = total_students * total_subjects

    results_percentage = round(
        (total_results / expected_results) * 100, 1
    ) if expected_results else 0

    students_percentage = min(round((total_students / 500) * 100, 1), 100)
    teachers_percentage = min(round((total_teachers / 50) * 100, 1), 100)

    return render(request, "admin_dashboard.html", {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_subjects": total_subjects,
        "total_classes": total_classes,
        "total_departments": total_departments,
        "total_notices": total_notices,
        "total_results": total_results,
        "results_percentage": results_percentage,
        "students_percentage": students_percentage,
        "teachers_percentage": teachers_percentage,
    })

def admin_logout(request):
    logout(request)
    return redirect('admin_login')

from django.urls import reverse
@login_required
def create_class(request):
    dashboard_url = reverse('admin_dashboard') if request.user.is_staff else reverse('teacher_dashboard')

    years = range(2022, 2031)

    if request.method == 'POST':
        class_name = request.POST.get('class_name')
        numeric_name = request.POST.get('numeric_name')
        level = request.POST.get('level')   # 🔹 NEW
        section = request.POST.get('section')
        session = request.POST.get('session')
        year = request.POST.get('year')

        if not all([class_name, numeric_name, level, section, session, year]):
            messages.error(request, 'All fields are required')
            return redirect('create_class')

        if int(year) < int(session):
            messages.error(request, 'Academic year cannot be earlier than intake year')
            return redirect('create_class')

        Class.objects.create(
            class_name=class_name,
            numeric_name=numeric_name,
            level=level,          # 🔹 NEW
            section=section,
            session=session,
            year=year
        )

        messages.success(request, 'Class successfully created')
        return redirect('create_class')

    return render(request, 'create_class.html', {
        'dashboard_url': dashboard_url,
        'years': years
    })

@login_required
def manage_classes(request):
    classes = Class.objects.all().order_by('numeric_name', 'class_name', 'section', 'level', 'year', 'session')
    return render(request, 'manage_classes.html', {'classes': classes})


@login_required
def edit_class(request, class_id):
    cls = get_object_or_404(Class, id=class_id)  # ✅ fixed

    if request.method == 'POST':
        cls.class_name = request.POST.get('class_name')
        cls.numeric_name = request.POST.get('numeric_name')
        cls.section = request.POST.get('section')
        cls.level = request.POST.get('level')
        cls.year = request.POST.get('year')
        cls.session = request.POST.get('session')

        cls.save()
        messages.success(request, "Class updated successfully")
        return redirect('manage_classes')

    return render(request, 'edit_class.html', {'cls': cls})


@login_required
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
def manage_subjects(request):
    user = request.user

    if hasattr(user, 'teacherprofile'):
        teacher = user.teacherprofile

        # Best approach: collect only valid departments (department2 optional)
        departments = list(
            filter(None, [teacher.department1, teacher.department2])
        )

        # If teacher has departments, filter by them; else show none
        subjects = (
            Subject.objects.filter(department__in=departments)
            if departments else Subject.objects.none()
        )

        dashboard_url = 'teacher_dashboard'
    else:
        # Admin access
        teacher = None
        subjects = Subject.objects.all()
        dashboard_url = 'admin_dashboard'

    context = {
        'teacher': teacher,
        'teacher_departments': departments if teacher else [],
        'subjects': subjects,
        'dashboard_url': dashboard_url,
    }

    return render(request, 'manage_subjects.html', context)

@login_required
def edit_subject(request, subject_id):
    cls = get_object_or_404(Subject, id= subject_id)
    if request.method == 'POST':
        cls.subject_name = request.POST.get('subject_name')
        cls.subject_code = request.POST.get('subject_code')
        cls.save()
        messages.success(request, 'Subject updated successfully')
        return redirect('manage_subjects')
    return render(request, 'edit_subject.html', {'cls': cls})

@login_required
def delete_subject(request, subject_id):
    cls = get_object_or_404(Subject, id=subject_id)
    cls.delete()
    messages.success(request, 'Subject deleted successfully')
    return redirect('manage_subjects')

@login_required
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

@login_required
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

@login_required
def delete_subject_combination(request, subject_id):  # <-- accept the argument
    combination = get_object_or_404(SubjectCombination, id=subject_id)

    if request.method == "POST":
        combination.delete()
        messages.success(request, "Subject combination deleted successfully")
        return redirect('manage_subject_combination')  # make sure this URL name exists
    
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Value, F
from django.db.models.functions import Concat

@login_required
def manage_students(request):
    query = request.GET.get('q')

    classes = Student.objects.annotate(
        student_name=Concat(F('first_name'), Value(' '), F('last_name'))
    )

    # 🔍 APPLY SEARCH
    if query:
        classes = classes.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(exam_no__icontains=query) |
            Q(address__icontains=query) |
            Q(student_class__class_name__icontains=query) |
            Q(student_class__numeric_name__icontains=query) |
            Q(student_class__section__icontains=query)
        )

    # 🔽 KEEP YOUR ORDERING
    classes = classes.order_by(
        'student_name', 'student_class', 'exam_no', 'phone_no',
        'gender', 'dob', 'address', 'parent_name', 'disability'
    )

    return render(request, 'manage_students.html', {'classes': classes})
from django.contrib.auth.models import User, Group
from django.contrib import messages
import secrets

def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)

            exam_no = student.exam_no  # ✅ use exam number

            # 🔴 CHECK if username already exists
            if User.objects.filter(username=exam_no).exists():
                messages.error(request, "Student with this Exam Number already exists.")
                return redirect('add_student')

            # 🔹 create user
            password = secrets.token_urlsafe(8)

            user = User.objects.create_user(
                username=exam_no,
                password=password,
                first_name=student.first_name,
                last_name=student.last_name,
            )

            # 🔹 assign to Students group
            students_group, _ = Group.objects.get_or_create(name='Students')
            user.groups.add(students_group)

            # 🔹 link user to student
            student.user = user
            student.save()

            messages.success(request, f"Student registered! Password: {password}")
            return redirect('manage_students')

        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StudentForm()

    return render(request, 'add_student.html', {'form': form})

@require_GET
def get_class_session(request):
    class_id = request.GET.get('class_id')

    if not class_id:
        return JsonResponse({'session': ''})

    try:
        student_class = Class.objects.get(id=class_id)
        return JsonResponse({
            'session': student_class.session
        })
    except Class.DoesNotExist:
        return JsonResponse({'session': ''})

@login_required
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    classes = Class.objects.all()  # all classes for the dropdown

    if request.method == 'POST':
        # Fetch POST data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        exam_no = request.POST.get('exam_no')
        phone_no = request.POST.get('phone_no')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        address = request.POST.get('address')
        parent_name = request.POST.get('parent_name')
        disability = request.POST.get('disability', 'none')
        class_id = request.POST.get('student_class')

        # Convert class_id to Class instance
        student_class_instance = get_object_or_404(Class, id=class_id)

        # Update student fields
        student.first_name = first_name
        student.last_name = last_name
        student.student_class = student_class_instance  # assign instance
        student.exam_no = exam_no
        student.phone_no = phone_no
        student.gender = gender
        student.dob = dob
        student.address = address
        student.parent_name = parent_name
        student.disability = disability

        student.save()
        messages.success(request, 'Student updated successfully')
        return redirect('manage_students')

    return render(request, 'edit_student.html', {
        'student': student,
        'classes': classes,
    })

@login_required
def delete_student(request, student_id):
    cls = get_object_or_404(Student, id=student_id)
    cls.delete()
    messages.success(request, 'Student deleted successfully')
    return redirect('manage_students')

def add_notice(request):
    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Notice added successfully!")
            return redirect('add_notice')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = NoticeForm()

    notices = Notice.objects.all().order_by('-posting_date')
    return render(request, 'ResultsApp/add_notice.html', {'form': form, 'notices': notices})

@login_required
def manage_notice(request):
    # Handle deletion via POST for better security
    if request.method == "POST" and "delete_id" in request.POST:
        notice_id = request.POST.get("delete_id")
        try:
            notice = Notice.objects.get(id=notice_id)
            notice.delete()
            messages.success(request, "Notice deleted successfully.")
        except Notice.DoesNotExist:
            messages.error(request, "Notice not found.")
        return redirect("manage_notice")

    # Fetch all notices, latest first
    notices = Notice.objects.all().order_by("-posting_date")

    return render(request, "ResultsApp/manage_notice.html", {"notices": notices})

@login_required
def edit_notice(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)

    if request.method == "POST":
        title = request.POST.get('title')
        details = request.POST.get('details')
        image = request.FILES.get('image')
        attachment = request.FILES.get('attachment')

        if not title:
            messages.error(request, "Title is required")
            return redirect('edit_notice', notice_id=notice_id)

        # Update fields
        notice.title = title
        notice.details = details

        # Update image if provided
        if image:
            notice.image = image

        # Update attachment if provided
        if attachment:
            notice.attachment = attachment

        notice.save()
        messages.success(request, "Notice updated successfully")
        return redirect('manage_notice')

    return render(request, "ResultsApp/edit_notice.html", {"notice": notice})

@login_required
def add_result(request):
    user = request.user
    is_admin = user.is_superuser

    # -------------------------------
    # Fetch Classes & Subjects
    # -------------------------------
    if not is_admin:
        teacher = user.teacherprofile

        # Department 2 is OPTIONAL (best approach)
        departments = list(filter(None, [
            teacher.department1,
            teacher.department2
        ]))

        classes = Class.objects.filter(
            subjectcombination__subject__department__in=departments
        ).distinct()

        subjects = Subject.objects.filter(
            department__in=departments
        )
    else:
        classes = Class.objects.all()
        subjects = Subject.objects.all()

    years = range(2020, 2031)
    current_year = timezone.now().year

    # -------------------------------
    # Handle Form Submission
    # -------------------------------
    if request.method == "POST":
        class_id = request.POST.get("class")
        subject_id = request.POST.get("subject")
        term = request.POST.get("term")
        academic_year = request.POST.get("year")
        test_type = request.POST.get("test_type")

        # Validation
        if not all([class_id, subject_id, term, academic_year, test_type]):
            messages.error(request, "All fields are required.")
            return redirect("add_result")

        selected_class = get_object_or_404(Class, id=class_id)
        selected_subject = get_object_or_404(Subject, id=subject_id)

        # -------------------------------
        # Department Security Check
        # -------------------------------
        if not is_admin:
            if selected_subject.department not in departments:
                messages.error(
                    request,
                    "You are not allowed to add results for this subject."
                )
                return redirect("add_result")

        # Redirect to marks entry page
        return redirect(
            "enter_marks",
            class_id=selected_class.id,
            subject_id=selected_subject.id,
            term=term,
            year=int(academic_year),
            test_type=test_type
        )

    # -------------------------------
    # Render Page
    # -------------------------------
    return render(request, "ResultsApp/add_result.html", {
        "classes": classes,
        "subjects": subjects,
        "years": years,
        "current_year": current_year,
        "is_admin": is_admin,
    })


# ----------------- ENTER MARKS -----------------
@login_required
def enter_marks(request, class_id, subject_id, term, year, test_type):
    selected_class = Class.objects.get(id=class_id)
    selected_subject = Subject.objects.get(id=subject_id)

    students = Student.objects.filter(student_class=selected_class)

    existing_results = {
        r.student_id: r.marks   # ✅ FIXED HERE
        for r in Result.objects.filter(
            student__in=students,
            subject_id=subject_id,
            term=term,
            test_type=test_type,
            year=year
        )
    }

    context = {
        'selected_class': selected_class,
        'selected_subject': selected_subject,
        'students': students,
        'existing_results': existing_results,
        'term': term,
        'test_type': test_type,
        'year': year,
        'session': selected_class.session,
    }

    return render(request, 'ResultsApp/enter_marks.html', context)


from django.http import JsonResponse
@login_required
def get_students_subjects(request):
    class_id = request.GET.get('class_id')

    if class_id:
        # Get students in this class and concatenate first_name and last_name
        students = Student.objects.filter(student_class_id=class_id).annotate(
            student_name=Concat(F('first_name'), Value(' '), F('last_name'))
        ).values('id', 'student_name', 'exam_no')

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

@login_required
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

    if not class_id:
        return JsonResponse({'subjects': []})

    class_instance = get_object_or_404(Class, id=class_id)

    # Subjects linked to this class
    subjects_in_class = Subject.objects.filter(
        subjectcombination__student_class=class_instance
    ).distinct()

    # -------------------------------
    # ADMIN → see everything
    # -------------------------------
    if user.is_superuser:
        subjects = subjects_in_class

    # -------------------------------
    # TEACHER → department-safe
    # -------------------------------
    else:
        teacher = user.teacherprofile

        # Department 2 OPTIONAL (BEST APPROACH)
        departments = list(filter(None, [
            teacher.department1,
            teacher.department2
        ]))

        subjects = subjects_in_class.filter(
            department__in=departments
        )

    subjects_list = [
        {
            'id': s.id,
            'name': s.subject_name,
            'code': s.subject_code
        }
        for s in subjects
    ]

    return JsonResponse({'subjects': subjects_list})

# Update results (AJAX POST)
from django.http import JsonResponse

@login_required
def update_results(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method."})

    # Get required POST data
    class_id = request.POST.get("class_id")
    subject_id = request.POST.get("subject_id")
    term = request.POST.get("term")
    test_type = request.POST.get("test_type")
    year = request.POST.get("year")

    if not all([class_id, subject_id, term, test_type, year]):
        return JsonResponse({"status": "error", "message": "Missing required fields."})

    students = Student.objects.filter(student_class_id=class_id)
    saved_count = 0

    for student in students:
        mark_str = request.POST.get(f"marks_{student.id}")

        if mark_str in [None, ""]:
            continue

        mark_str = mark_str.strip().lower()

        # ✅ Handle absence
        if mark_str in ["absent", "a"]:
            Result.objects.update_or_create(
                student=student,
                student_class_id=class_id,
                subject_id=subject_id,
                term=term,
                test_type=test_type,
                year=year,
                defaults={
                    "marks": None,
                    "is_absent": True
                }
            )
            saved_count += 1
            continue

        # ✅ Handle numeric marks
        try:
            mark = int(mark_str)
            if not (0 <= mark <= 100):
                continue
        except ValueError:
            continue

        Result.objects.update_or_create(
            student=student,
            student_class_id=class_id,
            subject_id=subject_id,
            term=term,
            test_type=test_type,
            year=year,
            defaults={
                "marks": mark,
                "is_absent": False
            }
        )
        saved_count += 1

    if saved_count == 0:
        return JsonResponse({"status": "error", "message": "No valid marks to save."})

    return JsonResponse({
        "status": "success",
        "message": f"Marks saved successfully for {saved_count} student(s)."
    })
    
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

    my_class = get_object_or_404(Class, id=class_id)
    subject = get_object_or_404(Subject, id=subject_id)
    students = Student.objects.filter(student_class=my_class).order_by('exam_no')

    # Initialize PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Results_{my_class}_{subject}_{term}_{year}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title = Paragraph(
        f"Class: {my_class.class_name} {my_class.numeric_name} {my_class.section} <br/>"
        f"Subject: {subject.subject_name} ({subject.subject_code}) <br/>"
        f"Test: {test_type} | Term: {term} | Year: {year}", 
        styles['Title']
    )
    elements.append(title)
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # Table data
    data = []  # ✅ initialize here
    # Header row
    data.append(['#', 'Student Name', 'Exam No', 'Gender', 'Marks'])

    # Student rows
    for idx, student in enumerate(students, start=1):
        result = Result.objects.filter(
            student=student,
            subject=subject,
            test_type=test_type,
            term=term,
            year=year
        ).first()
        marks = result.marks if result else ''
        # Use first_name and last_name instead of student_name
        full_name = f"{student.first_name} {student.last_name}"
        data.append([idx, full_name, student.exam_no, student.gender, marks])

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
    class_id = request.GET.get("class_id")
    subject_id = request.GET.get("subject_id")
    test_type = request.GET.get("test_type")
    term = request.GET.get("term")
    year = request.GET.get("year")

    if not all([class_id, subject_id, test_type, term, year]):
        return JsonResponse({"results": []})

    try:
        class_id = int(class_id)
        subject_id = int(subject_id)
        year = int(year)
    except ValueError:
        return JsonResponse({"results": []})

    # Get all students in the class
    students = Student.objects.filter(student_class_id=class_id)

    results_data = []

    for student in students:
        # Get existing result (no student_class filter)
        result = Result.objects.filter(
            student=student,
            subject_id=subject_id,
            test_type=test_type,
            term=term,
            year=year
        ).first()

        results_data.append({
            "student_id": student.id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "exam_no": student.exam_no,
            "marks": result.marks if result else ""
        })

    return JsonResponse({"results": results_data})


@csrf_protect
def teacher_login(request):
    # If user is already logged in
    if request.user.is_authenticated:
        try:
            teacher_profile = request.user.teacherprofile
            return redirect('teacher_dashboard')
        except TeacherProfile.DoesNotExist:
            # Logout non-teacher user to prevent redirect loop
            logout(request)
            messages.error(request, "You do not have a teacher profile. Please log in with a teacher account.")
            return redirect('teacher_login')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        # Authenticate user
        user = authenticate(request, username=email, password=password)

        if user is not None:
            try:
                teacher_profile = user.teacherprofile
                login(request, user)

                # Session expiry for "Remember Me"
                if remember_me:
                    request.session.set_expiry(604800)  # 7 days
                else:
                    request.session.set_expiry(0)       # Browser close

                return redirect('teacher_dashboard')

            except TeacherProfile.DoesNotExist:
                messages.error(request, "You do not have a teacher profile. Use a teacher account.")
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
@login_required
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
    return render(request, 'ResultsApp/edit_department.html', {'form': form})


# Delete department
@login_required
def delete_department(request, department_id):
    if request.method != "POST":
        raise Http404

    dept = get_object_or_404(Department, id=department_id)
    TeacherProfile.objects.filter(department=dept).update(department=None)
    Subject.objects.filter(department=dept).update(department=None)
    dept.delete()

    messages.success(request, "Department deleted successfully.")
    return redirect('manage_departments')

@login_required
def notice_detail(request, notice_id):
    # Get the notice object or show 404 if it doesn't exist
    notice = get_object_or_404(Notice, id=notice_id)
    return render(request, 'notice_detail.html', {'notice': notice})

def teacher_register(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            # Get user BEFORE saving (important)
            user = form.cleaned_data.get('user')

            # Check if profile already exists
            if TeacherProfile.objects.filter(user=user).exists():
                messages.error(request, "You already have a teacher profile.")
                return redirect('teacher_login')

            # Now save safely
            teacher = form.save()

            messages.success(
                request,
                f"Welcome {teacher.first_name}, your account has been created successfully."
            )
            return redirect('teacher_login')

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = TeacherRegistrationForm()

    return render(request, 'teacher_register.html', {
        'form': form
    })

from .models import TeacherProfile, Subject, Class, TeacherAssignment

from django.shortcuts import render, redirect
from django.contrib import messages

def assign_classes_subjects(request):
    teachers = TeacherProfile.objects.all()
    subjects = Subject.objects.all()
    classes = Class.objects.all()

    assignments = TeacherAssignment.objects.select_related(
        'teacher', 'subject', 'assigned_class'
    )

    if request.method == "POST":
        teacher_id = request.POST.get("teacher")
        subject_id = request.POST.get("subject")
        class_id = request.POST.get("class")

        obj, created = TeacherAssignment.objects.get_or_create(
            teacher_id=teacher_id,
            subject_id=subject_id,
            assigned_class_id=class_id
        )

        if created:
            messages.success(request, "Assignment added successfully")
        else:
            messages.warning(request, "This assignment already exists")

        return redirect('assign_classes_subjects')

    return render(request, 'admin/assign_classes_subjects.html', {
        'teachers': teachers,
        'subjects': subjects,
        'classes': classes,
        'assignments': assignments
    })

from django.shortcuts import get_object_or_404

def delete_assignment(request, id):
    assignment = get_object_or_404(TeacherAssignment, id=id)
    assignment.delete()
    messages.success(request, "Assignment deleted successfully")
    return redirect('assign_classes_subjects')

from django.db.models import Q
from django.db.models import Prefetch
from collections import defaultdict
from django.shortcuts import render
@login_required
def teacher_dashboard(request):
    teacher = request.user.teacherprofile

    # Fetch assignments for logged in teacher
    assignments = TeacherAssignment.objects.select_related(
        'assigned_class',
        'subject'
    ).filter(teacher=teacher)

    # Group assignments by class
    class_dict = defaultdict(lambda: {
        'class_obj': None,
        'subjects': []
    })

    for a in assignments:
        class_dict[a.assigned_class.id]['class_obj'] = a.assigned_class
        class_dict[a.assigned_class.id]['subjects'].append(a.subject)

    # Build context
    context = {
        'teacher': teacher,
        'class_data': class_dict.values(),
        'classes_count': len(class_dict),
        'subjects_count': assignments.count(),
        'students_count': sum(
            item['class_obj'].students.count()
            for item in class_dict.values()
            if item['class_obj']
        )
    }

    return render(request, 'teacher/dashboard.html', context)


def add_teacher(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            teacher = form.save()
            messages.success(request, f"Teacher {teacher.surname} {teacher.first_name} added successfully.")
            return redirect('manage_teachers')  # Make sure this URL name exists
        else:
            messages.error(request, "Please fix the errors below.")

    else:
        form = TeacherRegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'admin/add_teacher.html', context)


# ======= Manage Teachers =======
@login_required
def manage_teachers(request):
    teachers = TeacherProfile.objects.select_related(
        'user',
        'department1',
        'department2'
    ).prefetch_related('classes', 'subjects')

    return render(request, 'admin/manage_teachers.html', {
        'teachers': teachers
    })


# ======= Add Teacher =======
@login_required
def add_teacher(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            teacher = form.save()

            messages.success(
                request,
                f"Teacher {teacher.surname} {teacher.first_name} added successfully."
            )
            return redirect('manage_teachers')
        else:
            messages.error(request, "Please fix the errors below.")

    else:
        form = TeacherRegistrationForm()

    return render(request, 'admin/add_teacher.html', {
        'form': form
    })


# ======= Edit Teacher =======
@login_required
def edit_teacher(request, teacher_id):
    teacher = get_object_or_404(TeacherProfile, id=teacher_id)

    if request.method == 'POST':
        form = TeacherRegistrationForm(
            request.POST,
            request.FILES,
            instance=teacher
        )

        if form.is_valid():
            teacher_profile = form.save()  # FORM already handles user + password

            messages.success(
                request,
                f"Teacher {teacher_profile.surname} {teacher_profile.first_name} updated successfully!"
            )
            return redirect('manage_teachers')
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = TeacherRegistrationForm(instance=teacher)

    return render(request, 'admin/edit_teacher.html', {
        'form': form,
        'teacher': teacher
    })



# ======= Delete Teacher =======
@login_required
def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(TeacherProfile, id=teacher_id)

    # Deletes the linked User as well
    if teacher.user:
        teacher.user.delete()
    teacher.delete()

    messages.success(request, "Teacher deleted successfully.")
    return redirect('manage_teachers')

@login_required
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

@login_required
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


def class_list_view(request):
    classes = Class.objects.all()
    return render(request, 'class_list.html', {'classes': classes})


# ------------------- Load Students via AJAX -------------------
def get_class_details(request):
    class_id = request.GET.get('class_id')
    if not class_id:
        return JsonResponse({})

    try:
        cls = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return JsonResponse({})

    students = Student.objects.filter(student_class=cls).values(
        'id', 'first_name', 'last_name', 'gender', 'disability', 'address', 'exam_no'
    )

    students_list = []
    for i, s in enumerate(students, start=1):
        students_list.append({
            's_no': i,
            'student_name': f"{s['first_name']} {s['last_name']}",
            'gender': s['gender'],
            'disability': s['disability'],
            'address': s['address'],
            'exam_no': s['exam_no'],
        })

    # Concatenate full class name
    full_class_name = f"{cls.class_name} {cls.numeric_name} {cls.section}"

    return JsonResponse({
        'full_class_name': full_class_name,  # concatenated class name
        'session': cls.session,           # session
        'year': cls.year,            # academic year
        'students': students_list
    })


# ------------------- Download Class List as CSV -------------------
def download_class_list(request, class_id):
    cls = get_object_or_404(Class, id=class_id)
    students = Student.objects.filter(student_class=cls)

    response = HttpResponse(content_type='text/csv')
    full_class_name = f"{cls.class_name} {cls.numeric_name} {cls.section}"
    response['Content-Disposition'] = f'attachment; filename="{full_class_name}_class_list.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'S.No', 'Student Name', 'Gender', 'Disability', 'Address', 'Exam Number'
    ])

    for idx, student in enumerate(students, start=1):
        student_name = f"{student.first_name} {student.last_name}"
        writer.writerow([
            idx,
            student_name,
            student.gender,
            student.disability,
            student.address,
            student.exam_no
        ])

    return response


@login_required
def mark_schedule_view(request):
    classes = Class.objects.all().order_by('class_name', 'numeric_name', 'section')

    class_id = request.GET.get('class')
    term = request.GET.get('term')
    test_type = request.GET.get('test_type', 'ALL')
    selected_subjects = request.GET.getlist('subjects')

    students = Student.objects.none()
    subjects = SubjectCombination.objects.none()
    all_subjects = SubjectCombination.objects.none()
    marks_dict = {}

    selected_class = None

    if class_id:
        selected_class = get_object_or_404(Class, id=class_id)

        # ✅ Subjects ONLY for selected class (checkbox list)
        all_subjects = SubjectCombination.objects.filter(
            student_class=selected_class,
            status=1
        ).select_related('subject')

        # Students
        if term:
            students = Student.objects.filter(
                student_class=selected_class,
                status=1
            ).order_by('first_name')

            # Apply subject filter
            subjects = all_subjects
            if selected_subjects:
                subjects = subjects.filter(subject__id__in=selected_subjects)

            # Results
            results = Result.objects.filter(
                student_class=selected_class,
                term=term,
                year=selected_class.year
            )

            if test_type != "ALL":
                results = results.filter(test_type=test_type)

            for r in results:
                if not selected_subjects or str(r.subject_id) in selected_subjects:
                    marks_dict \
                        .setdefault(r.student_id, {}) \
                        .setdefault(r.subject_id, {})[r.test_type] = r.marks

    return render(request, 'mark_schedule.html', {
        'classes': classes,
        'students': students,
        'subjects': subjects,
        'all_subjects': all_subjects,
        'marks_dict': marks_dict,
        'selected_class': selected_class,
        'selected_test_type': test_type,
        'selected_term': term,
        'selected_subjects': selected_subjects,
    })

@login_required
def download_mark_schedule_pdf(request):
    class_id = request.GET.get('class')
    term = request.GET.get('term')
    test_type = request.GET.get('test_type', 'ALL')
    selected_subject_ids = request.GET.getlist('subjects')  # Multi-select subjects

    if not class_id or not term:
        messages.error(request, "Class and Term are required to generate PDF.")
        return redirect('mark_schedule_view')  # Adjust to your URL

    selected_class = Class.objects.get(id=class_id)
    students = Student.objects.filter(student_class=selected_class, status=1).order_by('first_name')

    # ---------- FILTER SUBJECTS ----------
    subjects_qs = SubjectCombination.objects.filter(student_class=selected_class, status=1).select_related('subject')
    if selected_subject_ids:
        subjects_qs = subjects_qs.filter(subject_id__in=selected_subject_ids)

    # ---------- FILTER RESULTS ----------
    results = Result.objects.filter(student_class=selected_class, term=term, year=selected_class.year)
    if selected_subject_ids:
        results = results.filter(subject_id__in=selected_subject_ids)

    # ---------- PREPARE MARKS DICTIONARY ----------
    marks_dict = {}
    for r in results:
        marks_dict.setdefault(r.student_id, {}).setdefault(r.subject_id, {})[r.test_type] = r.marks

    # ---------- PAGE ORIENTATION ----------
    num_columns = 4 + len(subjects_qs) * (3 if test_type == "ALL" else 1)
    page_size = landscape(A4) if num_columns > 8 else A4

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mark_schedule.pdf"'

    doc = SimpleDocTemplate(response, pagesize=page_size, rightMargin=20, leftMargin=20, topMargin=50, bottomMargin=20)
    elements = []

    # ---------- STYLES ----------
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontSize=14, alignment=1, spaceAfter=5)
    normal_center = ParagraphStyle('NormalCenter', parent=styles['Normal'], fontSize=11, alignment=1, spaceAfter=3)

    # ---------- LOGOS ----------
    school_logo_path = os.path.join(settings.BASE_DIR, 'ResultsApp', 'static', 'images', 'logo.png')
    school_logo = RLImage(school_logo_path, width=40, height=40) if os.path.isfile(school_logo_path) else Paragraph("", normal_center)
    ministry_logo_path = os.path.join(settings.BASE_DIR, 'ResultsApp', 'static', 'images', 'ministry_logo.png')
    ministry_logo = RLImage(ministry_logo_path, width=40, height=40) if os.path.isfile(ministry_logo_path) else Paragraph("", normal_center)

    # ---------- HEADER ----------
    header_title = Paragraph("<b>MUYOMBE DAY SECONDARY SCHOOL</b>", title_style)
    header_table = Table([[school_logo, header_title, ministry_logo]], colWidths=[50, None, 50])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('ALIGN', (2,0), (2,0), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(header_table)

    # ---------- HEADER INFO ----------
    header_text = f"""
        Class: {selected_class.class_name} {selected_class.numeric_name} {selected_class.section}<br/>
        Term: {term} | Test Type: {test_type}<br/>
        Session: {selected_class.session} | Academic Year: {selected_class.year}
    """
    elements.append(Paragraph(header_text, normal_center))
    elements.append(Spacer(1, 12))

    # ---------- TABLE HEADER ----------
    table_data = []

    # First row: S/No, Exam No, Student Name, Gender + subject names (merged later)
    first_row = ["S/No", "Exam No", "Student Name", "Gender"]
    second_row = ["", "", "", ""]  # empty for the first 4 columns

    for sc in subjects_qs:
        if test_type == "ALL":
            first_row.extend([sc.subject.subject_name] + ["", ""])  # placeholder for colspan
            second_row.extend(["T1", "T2", "EOT"])
        else:
            first_row.append(sc.subject.subject_name)
            second_row.append(test_type)

    table_data.append(first_row)
    if test_type == "ALL":
        table_data.append(second_row)

    # ---------- TABLE ROWS ----------
    for idx, student in enumerate(students, 1):
        row = [idx, student.exam_no, f"{student.first_name} {student.last_name}", student.gender]
        for sc in subjects_qs:
            if test_type == "ALL":
                row.extend([
                    marks_dict.get(student.id, {}).get(sc.subject.id, {}).get("TEST1", "-"),
                    marks_dict.get(student.id, {}).get(sc.subject.id, {}).get("TEST2", "-"),
                    marks_dict.get(student.id, {}).get(sc.subject.id, {}).get("EOT", "-")
                ])
            else:
                row.append(marks_dict.get(student.id, {}).get(sc.subject.id, {}).get(test_type, "-"))
        table_data.append(row)

    # ---------- COLUMN WIDTHS ----------
    col_widths = [1.2*cm, 2.5*cm, 4*cm, 2*cm] + [2*cm for _ in range(len(table_data[0])-4)]

    # ---------- CREATE TABLE ----------
    table = Table(table_data, repeatRows=2 if test_type == "ALL" else 1, colWidths=col_widths, hAlign='CENTER')

    # ---------- TABLE STYLE ----------
    style_commands = [
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
    ]

    # ---------- MERGE CELLS FOR SUBJECTS (span 3 columns if ALL test types) ----------
    if test_type == "ALL":
        col_index = 4  # starting after the first 4 columns
        for sc in subjects_qs:
            style_commands.append(('SPAN', (col_index,0), (col_index+2,0)))  # merge 3 columns for subject
            col_index += 3

    table.setStyle(TableStyle(style_commands))
    elements.append(table)

    # ---------- BUILD PDF ----------
    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return response


@login_required
def download_mark_schedule_excel(request):
    class_id = request.GET.get('class')
    term = request.GET.get('term')
    test_type = request.GET.get('test_type', 'ALL')

    selected_class = Class.objects.get(id=class_id)
    students = Student.objects.filter(student_class=selected_class, status=1).order_by('first_name')
    subjects = SubjectCombination.objects.filter(student_class=selected_class, status=1).select_related('subject')
    results = Result.objects.filter(student_class=selected_class, term=term, year=selected_class.year)
    if test_type != "ALL":
        results = results.filter(test_type=test_type)

    marks_dict = {}
    for r in results:
        marks_dict.setdefault(r.student_id, {}).setdefault(r.subject_id, {})[r.test_type] = r.marks

    wb = Workbook()
    ws = wb.active
    ws.title = "Mark Schedule"

    # ---------- SCHOOL HEADER ----------
    ws.merge_cells('A1:D1')
    ws['A1'] = "Joy High School"
    ws['A1'].font = Font(bold=True, size=14)
    ws['A1'].alignment = Alignment(horizontal='center')
    
    ws.merge_cells('A2:D2')
    ws['A2'] = f"Class: {selected_class.class_name} {selected_class.numeric_name} {selected_class.section} | Term: {term} | Test Type: {test_type} | Session: {selected_class.session} | Academic Year: {selected_class.year}"
    ws['A2'].alignment = Alignment(horizontal='center')

    # ---------- TABLE HEADER ----------
    header = ["S/No", "Exam No", "Student Name", "Gender"]
    for sc in subjects:
        if test_type == "ALL":
            header.extend([f"{sc.subject.subject_name} T1", f"{sc.subject.subject_name} T2", f"{sc.subject.subject_name} EOT"])
        else:
            header.append(sc.subject.subject_name)
    ws.append(header)

    # ---------- TABLE ROWS ----------
    for idx, student in enumerate(students, 1):
        row = [idx, student.exam_no, f"{student.first_name} {student.last_name}", student.gender]
        for sc in subjects:
            if test_type == "ALL":
                row.extend([
                    marks_dict.get(student.id, {}).get(sc.subject.id, {}).get("TEST1", "-"),
                    marks_dict.get(student.id, {}).get(sc.subject.id, {}).get("TEST2", "-"),
                    marks_dict.get(student.id, {}).get(sc.subject.id, {}).get("EOT", "-")
                ])
            else:
                row.append(marks_dict.get(student.id, {}).get(sc.subject.id, {}).get(test_type, "-"))
        ws.append(row)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=mark_schedule.xlsx'
    wb.save(response)
    return response


@login_required
def download_term_mark_schedule_pdf(request):
    request.GET._mutable = True
    request.GET['test_type'] = 'ALL'
    return download_mark_schedule_pdf(request)

def add_page_number(canvas_obj, doc):
    page_num = canvas_obj.getPageNumber()
    text = f"Page {page_num}"
    canvas_obj.setFont('Helvetica', 9)
    canvas_obj.drawRightString(200*mm, 10*mm, text)

# ------------------ STAFF LIST VIEW ------------------
@login_required
def staff_list(request):
    """Render all teachers in a table with download links."""
    # Annotate full_name instead of using non-existent teacher_name
    teachers = TeacherProfile.objects.annotate(
        full_name=Concat(
            F('surname'), Value(' '),
            F('first_name'), Value(' '),
            F('other_names'),
            output_field=CharField()
        )
    ).order_by('full_name')
    return render(request, 'staff_list.html', {'teachers': teachers})


# ------------------ EXCEL EXPORT ------------------
@login_required
def staff_list_excel(request):
    """Export all teachers to Excel."""
    teachers = TeacherProfile.objects.annotate(
        full_name=Concat(
            F('surname'), Value(' '),
            F('first_name'), Value(' '),
            F('other_names'),
            output_field=CharField()
        )
    ).values(
        'full_name',
        'gender',
        'marital_status',
        'phone_no',

        'department1__department_name',
        'department2__department_name',

        'academic_qualification',
        'professional_qualification',
        'minor',
        'major',

        'date_first_app',
        'date_current_app',
        'date_of_retirement',

        'NRC_No',
        'TCZ_No',
        'TS_No',
        'Employ_No',
        'disability',
        'current_station',
        'pay_point',
        'district_of_pay_point',
        'bank_name',
        'account_number',
        'branch_name',
        'substantive_position',
        'current_position',
        'year_of_graduation',
        'college_university',
        'confirmed',
        'next_of_kin_name',
        'next_of_kin_phone',
        'next_of_kin_relationship',
        'next_of_kin_district',
        'distance_from_DEBs',
        'salary_scale'
    )

    df = pd.DataFrame(list(teachers))
    df.rename(columns={
        'full_name': 'Name',
        'department1__department_name': 'Department 1',
        'department2__department_name': 'Department 2',
        'phone_no': 'Phone',
        'date_first_app': 'First Appointment',
        'date_current_app': 'Current Appointment',
        'date_of_retirement': 'Retirement Date',
        'current_station': 'Current Station',
        'pay_point': 'Pay Point',
        'district_of_pay_point': 'District of Pay Point',
        'bank_name': 'Bank Name',
        'account_number': 'Account No',
        'branch_name': 'Branch Name',
        'substantive_position': 'Substantive Position',
        'current_position': 'Current Position',
        'year_of_graduation': 'Year of Graduation',
        'college_university': 'College/University',
        'confirmed': 'Confirmed',
        'next_of_kin_name': 'Next of Kin Name',
        'next_of_kin_phone': 'Next of Kin Phone',
        'next_of_kin_relationship': 'Next of Kin Relationship',
        'next_of_kin_district': 'Next of Kin District',
        'distance_from_DEBs': 'Distance from DEBs (km)',
        'salary_scale': 'Salary Scale'
    }, inplace=True)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="staff_list.xlsx"'
    df.to_excel(response, index=False)
    return response


@login_required
def staff_list_pdf(request):
    """Export all teachers to PDF in landscape with wrapped cells and adjustable font."""

    # Annotate full_name and order by it
    teachers = TeacherProfile.objects.annotate(
        full_name=Concat(
            F('surname'), Value(' '),
            F('first_name'), Value(' '),
            F('other_names'),
            output_field=CharField()
        )
    ).order_by('full_name')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="staff_list.pdf"'

    # Use landscape orientation
    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        rightMargin=10*mm,
        leftMargin=10*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )

    elements = []
    styles = getSampleStyleSheet()
    wrap_style = ParagraphStyle(
        name='wrap',
        fontSize=7,
        leading=9,  # line height
        alignment=1,  # center alignment
        spaceAfter=0,
        spaceBefore=0
    )

    # ---------- HEADER ----------
    header_style = ParagraphStyle(
        'header',
        parent=styles['Title'],
        alignment=1,  # center
        fontSize=14,
        spaceAfter=10
    )
    elements.append(Paragraph("<b>Staff List - Joy High School</b>", header_style))
    elements.append(Spacer(1, 6))

    # ---------- TABLE DATA ----------
    columns = [
        "S/No", "Name", "Gender", "Marital Status", "Phone",
        "Department 1", "Department 2", "Current Station", "Pay Point", "District of Pay Point",
        "Bank Name", "Account No", "Branch Name",
        "Academic Qualification", "Professional Qualification", "Major", "Minor",
        "First Appointment", "Substantive Position", "Current Position", "Current Appointment", "Retirement Date",
        "Year of Graduation", "College/University", "Confirmed",
        "Next of Kin Name", "Next of Kin Phone", "Next of Kin Relationship", "Next of Kin District",
        "NRC", "TCZ", "TS", "Employ No", "Disability", "Distance from DEBs (km)", "Salary Scale"
    ]

    table_data = [[Paragraph(col, wrap_style) for col in columns]]

    for idx, teacher in enumerate(teachers, 1):
        row = [
            Paragraph(str(idx), wrap_style),
            Paragraph(teacher.full_name or '-', wrap_style),
            Paragraph(teacher.gender or '-', wrap_style),
            Paragraph(teacher.marital_status or '-', wrap_style),
            Paragraph(teacher.phone_no or '-', wrap_style),
            Paragraph(teacher.department1.department_name if teacher.department1 else '-', wrap_style),
            Paragraph(teacher.department2.department_name if teacher.department2 else '-', wrap_style),
            Paragraph(teacher.current_station or '-', wrap_style),
            Paragraph(teacher.pay_point or '-', wrap_style),
            Paragraph(teacher.district_of_pay_point or '-', wrap_style),
            Paragraph(teacher.bank_name or '-', wrap_style),
            Paragraph(teacher.account_number or '-', wrap_style),
            Paragraph(teacher.branch_name or '-', wrap_style),
            Paragraph(teacher.academic_qualification or '-', wrap_style),
            Paragraph(teacher.professional_qualification or '-', wrap_style),
            Paragraph(teacher.major or '-', wrap_style),
            Paragraph(teacher.minor or '-', wrap_style),
            Paragraph(teacher.date_first_app.strftime("%d-%m-%Y") if teacher.date_first_app else '-', wrap_style),
            Paragraph(teacher.substantive_position or '-', wrap_style),
            Paragraph(teacher.current_position or '-', wrap_style),
            Paragraph(teacher.date_current_app.strftime("%d-%m-%Y") if teacher.date_current_app else '-', wrap_style),
            Paragraph(teacher.date_of_retirement.strftime("%d-%m-%Y") if teacher.date_of_retirement else '-', wrap_style),
            Paragraph(teacher.year_of_graduation or '-', wrap_style),
            Paragraph(teacher.college_university or '-', wrap_style),
            Paragraph(str(teacher.confirmed or '-'), wrap_style),
            Paragraph(teacher.next_of_kin_name or '-', wrap_style),
            Paragraph(teacher.next_of_kin_phone or '-', wrap_style),
            Paragraph(teacher.next_of_kin_relationship or '-', wrap_style),
            Paragraph(teacher.next_of_kin_district or '-', wrap_style),
            Paragraph(teacher.NRC_No or '-', wrap_style),
            Paragraph(teacher.TCZ_No or '-', wrap_style),
            Paragraph(teacher.TS_No or '-', wrap_style),
            Paragraph(teacher.Employ_No or '-', wrap_style),
            Paragraph(teacher.disability or '-', wrap_style),
            Paragraph(str(teacher.distance_from_DEBs or '-'), wrap_style),
            Paragraph(teacher.salary_scale or '-', wrap_style)
        ]
        table_data.append(row)

    # ---------- CREATE TABLE ----------
    col_widths = [
        8*mm, 30*mm, 12*mm, 18*mm, 20*mm, 20*mm, 20*mm, 20*mm, 18*mm, 22*mm,
        22*mm, 22*mm, 20*mm, 20*mm, 20*mm, 18*mm, 18*mm, 18*mm, 20*mm, 20*mm,
        20*mm, 20*mm, 20*mm, 18*mm, 22*mm, 18*mm, 20*mm, 18*mm, 18*mm, 18*mm,
        18*mm, 18*mm, 18*mm, 18*mm, 18*mm, 18*mm
    ]

    table = Table(table_data, repeatRows=1, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4BACC6")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7),
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#EAF1F8")])
    ]))
    elements.append(table)

    # ---------- PAGE NUMBER ----------
    def add_page_number(canvas, doc):
        canvas.saveState()
        page_num = canvas.getPageNumber()
        canvas.setFont('Helvetica', 7)
        canvas.drawRightString(landscape(A4)[0] - 10*mm, 10*mm, f"Page {page_num}")
        canvas.restoreState()

    # Build PDF
    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return response

@login_required
def report_form_select_class(request):
    classes = Class.objects.all().order_by("level", "numeric_name")

    # Fetch distinct test types from Result table
    test_types = (
        Result.objects
        .values_list("test_type", flat=True)
        .distinct()
        .order_by("test_type")
    )

    return render(request, "report_form_select_class.html", {
    "classes": classes,
    "test_choices": Result.TEST_CHOICES,
    "term_choices": Result.TERM_CHOICES,
})

def get_grade_comment(class_level, mark):
    if mark is None:
        return "X", "ABSENT"

    try:
        grading_system = GradingSystem.objects.get(class_level=class_level)
    except GradingSystem.DoesNotExist:
        return "-", "NO GRADING SYSTEM"

    grade_rule = (
        Grade.objects
        .filter(grading_system=grading_system, min_mark__lte=mark)
        .order_by("-min_mark")
        .first()
    )

    if grade_rule:
        return grade_rule.grade, grade_rule.comment

    return "F", "FAIL"


# View to select class, term, and test type
@login_required
def report_form_select_class(request):
    classes = Class.objects.all().order_by("level", "numeric_name")
    test_choices = Result.TEST_CHOICES
    term_choices = Result.TERM_CHOICES

    return render(request, "report_form_select_class.html", {
        "classes": classes,
        "test_choices": test_choices,
        "term_choices": term_choices,
    })


# View to generate PDF report forms
from django.utils.timezone import now
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
import os
from django.templatetags.static import static
from django.contrib.staticfiles import finders

def generate_stamp_with_date(date_text):
    import os
    from django.conf import settings
    from PIL import Image, ImageDraw, ImageFont

    from django.contrib.staticfiles import finders

    stamp_path = finders.find("images/head_stamp.png")
    output_filename = f"stamp_{date_text.replace(' ', '_')}.png"
    output_path = os.path.join(settings.MEDIA_ROOT, output_filename)

    image = Image.open(stamp_path).convert("RGBA")
    draw = ImageDraw.Draw(image)

    # Font path
    font_path = os.path.join(settings.BASE_DIR, "static/fonts/arial.ttf")

    # ✅ Safe font loading
    try:
        font = ImageFont.truetype(font_path, 22)
    except IOError:
        font = ImageFont.load_default()

    # Image size
    img_width, img_height = image.size

    # Measure text
    bbox = draw.textbbox((0, 0), date_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Define rectangle area
    rect_x1 = int(img_width * 0.25)
    rect_y1 = int(img_height * 0.40)
    rect_x2 = int(img_width * 0.75)
    rect_y2 = int(img_height * 0.65)

    # Center text
    x = rect_x1 + (rect_x2 - rect_x1 - text_width) // 2
    y = rect_y1 + (rect_y2 - rect_y1 - text_height) // 2

    # Draw text
    draw.text((x, y), date_text, fill="black", font=font)

    if not os.path.exists(output_path):
     image.save(output_path)

    return settings.MEDIA_URL + output_filename

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.utils.timezone import now
from django.conf import settings

from weasyprint import HTML

from io import BytesIO
import os


# ✅ Handles static + media files for WeasyPrint
def weasyprint_url_fetcher(url):
    if url.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, url.replace(settings.MEDIA_URL, ""))
        return {'file_obj': open(path, 'rb')}

    if url.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, url.replace(settings.STATIC_URL, ""))
        return {'file_obj': open(path, 'rb')}

    return {}


@login_required
def report_form_generator(request):
    if request.method == "POST":
        class_id = request.POST.get("class_id")
        term = request.POST.get("term")
        test_type = request.POST.get("test_type")

        if not all([class_id, term, test_type]):
            return HttpResponse("Missing required fields", status=400)

        cls = Class.objects.get(id=class_id)

        students = Student.objects.filter(
            student_class=cls
        ).order_by("last_name", "first_name")

        html_pages = []

        # ✅ Generate date ONCE
        report_date = now().strftime("%d %B %Y")

        # ✅ Generate stamp ONCE
        generated_stamp = generate_stamp_with_date(report_date)

        for student in students:
            results_qs = Result.objects.filter(
                student=student,
                term=term,
                test_type=test_type
            ).select_related("subject")

            results_data = []

            for res in results_qs:
                if res.is_absent:
                    mark_display = "A"
                    grade = "-"
                    comment = "Absent"
                else:
                    mark_display = res.marks
                    grade, comment = get_grade_comment(cls.level, res.marks)

                results_data.append({
                    "subject": res.subject.subject_name if res.subject else "N/A",
                    "mark": mark_display,
                    "grade": grade,
                    "comment": comment,
                })

            teacher_comment, head_comment = generate_teacher_head_comments(results_data)

            # ✅ Render HTML per student
            html = render_to_string("ecz_report_form.html", {
                "student": student,
                "cls": cls,
                "term": term,
                "test_type": test_type,
                "results": results_data,
                "teacher_comment": teacher_comment,
                "head_comment": head_comment,
                "report_date": report_date,
                "head_signature": static("images/head_signature.png"),
                "head_stamp": generated_stamp,
            })

            html_pages.append(html)

        # ✅ Combine pages
        final_html = '<div style="page-break-after: always;"></div>'.join(html_pages)

        # ✅ Generate PDF using WeasyPrint
        pdf_file = BytesIO()

        HTML(
            string=final_html,
            base_url=request.build_absolute_uri("/")  # VERY IMPORTANT
        ).write_pdf(
            target=pdf_file,
            url_fetcher=weasyprint_url_fetcher
        )

        response = HttpResponse(pdf_file.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="BupeSmart_Report_{cls.class_name}.pdf"'
        )

        return response

    else:
        classes = Class.objects.all().order_by("level", "numeric_name")
        test_choices = Result.TEST_CHOICES
        term_choices = Result.TERM_CHOICES

        return render(request, "report_form_select_class.html", {
            "classes": classes,
            "test_choices": test_choices,
            "term_choices": term_choices,
        })
    
def generate_teacher_head_comments(results):
    """
    results: list of dicts with keys: 'subject', 'mark', 'grade', 'comment'
    """
    grades = [r['grade'] for r in results if r['grade'] not in ['X', '-', None]]
    
    if not grades:
        return "No marks available.", "No marks available."
    
    # Class teacher comment
    if all(g in ['A+', 'A', 'A-', 'B+','B'] for g in grades):
        teacher_comment = "Excellent performance. Keep it up!"
        head_comment = "Outstanding overall performance."
    elif any(g in ['F', 'E'] for g in grades):
        teacher_comment = "Student needs to work extra hard."
        head_comment = "Student requires intervention and support."
    else:
        teacher_comment = "Good effort. Needs improvement in some subjects."
        head_comment = "Satisfactory performance. Focus on weaker areas."

    return teacher_comment, head_comment

def get_grade(marks, grading_system):
    """
    Returns the grade string for given marks according to the class level grading system.
    grading_system: GradingSystem instance
    """
    grade = grading_system.grades.filter(min_mark__lte=marks).order_by('-min_mark').first()
    if grade:
        return grade.grade
    return None


from django.http import JsonResponse, HttpResponseForbidden
User = get_user_model()

# ---------------------------
# MESSAGES
# ---------------------------

@login_required
def message_recipients(request):
    """Return all admins + teachers except current user."""
    users = User.objects.filter(
        is_active=True
    ).filter(
        Q(is_staff=True) | Q(teacherprofile__isnull=False)
    ).exclude(id=request.user.id)

    users_data = [{'id': u.id, 'username': u.username} for u in users]
    return JsonResponse({'users': users_data})


# ---------------------------
# Send message
# ---------------------------
@login_required
def send_message(request):
    """Send message via form or AJAX."""
    if request.method == "POST":
        # JSON/AJAX
        if request.content_type == "application/json":
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)
            recipient_id = data.get("recipient")
            subject = data.get("subject", "").strip()
            body = data.get("body", "").strip()
        else:
            # Standard form POST
            recipient_id = request.POST.get("recipient")
            subject = request.POST.get("subject", "").strip()
            body = request.POST.get("body", "").strip()

        # Validate
        if not recipient_id or not subject or not body:
            return JsonResponse({"error": "All fields are required"}, status=400)

        try:
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "Recipient not found"}, status=404)

        if recipient.id == request.user.id:
            return JsonResponse({"error": "Cannot send message to yourself"}, status=400)

        # Create Message
        message = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            subject=subject,
            body=body,
            timestamp=timezone.now()
        )

        # Create Notification for recipient
        Notification.objects.create(
            user=recipient,
            message=f"New message from {request.user.username}: {subject}",
            link="/messages/inbox/",
            timestamp=timezone.now()
        )

        return JsonResponse({"success": True, "message": "Message sent"})

    # GET: render send message page
    return render(request, "send_message.html")


# ---------------------------
# Inbox messages
# ---------------------------
from django.utils.timesince import timesince

from django.utils.timezone import localtime

@login_required
def recent_messages(request):
    """Return recent 10 messages for navbar or inbox AJAX."""
    messages_qs = Message.objects.filter(recipient=request.user).order_by('-timestamp')[:10]
    
    data = {
        "messages": [
            {
                "id": m.id,
                "sender": m.sender.username,
                "sender_id": m.sender.id,
                "subject": m.subject,
                "body": m.body,
                "timestamp": m.timestamp.strftime("%Y-%m-%d %H:%M"),
                "is_read": m.is_read,
            } for m in messages_qs
        ],
        "unread_count": Message.objects.filter(recipient=request.user, is_read=False).count()
    }
    return JsonResponse(data)

# ---------------------------
# Sent messages
# ---------------------------
@login_required
@csrf_exempt
def sent_messages(request):
    """Fetch messages sent BY the logged-in user."""
    messages_qs = Message.objects.filter(sender=request.user).order_by('-timestamp')[:10]
    messages_list = [{
        'id': m.id,
        'recipient': m.recipient.username,
        'subject': m.subject,
        'timestamp': m.timestamp.strftime('%d %b %Y %H:%M')
    } for m in messages_qs]

    return JsonResponse({'messages': messages_list})

# ---------------------------
# Delete message (sender only)
# ---------------------------

@login_required
@csrf_exempt
def delete_message(request, message_id):
    if request.method == "POST":
        try:
            msg = Message.objects.get(id=message_id)
            if msg.recipient != request.user and msg.sender != request.user:
                return JsonResponse({"success": False, "error": "Not allowed"}, status=403)
            msg.delete()
            return JsonResponse({"success": True})
        except Message.DoesNotExist:
            return JsonResponse({"success": False, "error": "Message not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})


# Notifications
# ---------------------------
@login_required
def unread_notifications(request):
    """Return unread notifications for the user."""
    notifs = Notification.objects.filter(user=request.user, is_read=False).order_by('-timestamp')[:10]
    notif_list = [{
        'id': n.id,
        'message': n.message,
        'link': n.link,
        'timestamp': n.timestamp.strftime('%d %b %Y %H:%M')
    } for n in notifs]
    return JsonResponse({'notifications': notif_list, 'unread_count': notifs.count()})


@login_required
def inbox(request):
    """Inbox page for logged-in user."""
    # Get all messages for this user
    messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')

    # Users for sending messages (teachers + staff)
    staff_users = User.objects.filter(
        Q(is_staff=True) | Q(teacherprofile__isnull=False),
        is_active=True
    ).exclude(id=request.user.id)

    return render(request, "ResultsApp/inbox.html", {
        "messages": messages,
        "staff_users": staff_users,
    })


@login_required
@csrf_exempt
def view_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    if message.recipient != request.user:
        return HttpResponseForbidden()
    message.is_read = True
    message.save()
    return render(request, "view_message.html", {"message": message})


from .models import Message  # make sure this is your message model


@login_required
@csrf_exempt
def mark_message_read(request, message_id):
    """Mark a message as read for recipient."""
    if request.method == "POST":
        updated = Message.objects.filter(id=message_id, recipient=request.user, is_read=False).update(is_read=True)
        return JsonResponse({"success": bool(updated)})
    return JsonResponse({"success": False, "error": "Invalid method"})



@login_required
@csrf_exempt
def clear_messages(request):
    if request.method == "POST":
        Message.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"})


# ---------------------------
# NOTIFICATIONS
# ---------------------------

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-timestamp')

    if request.method == "POST" and "clear_notifications" in request.POST:
        notifications.update(is_read=True)
        return redirect("notifications_view")

    return render(request, "notifications/notifications.html", {
        "notifications": notifications
    })

@login_required
def mark_notification_read(request, pk):
    Notification.objects.filter(
        id=pk,
        user=request.user
    ).update(is_read=True)
    return JsonResponse({"success": True})

from .models import Notification


@login_required
@csrf_exempt
def clear_notifications(request):
    if request.method == "POST":
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"})


@login_required
def recent_notifications(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-timestamp')[:10]

    unread_count = notifications.filter(is_read=False).count()

    return JsonResponse({
        "unread_count": unread_count,
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "is_read": n.is_read,
                "timestamp": n.timestamp.strftime("%d %b %Y %H:%M"),
                "link": n.link
            } for n in notifications
        ]
    })

def message_recipients(request):
    # Only teachers for admin
    teachers = TeacherProfile.objects.all()
    users_data = [{'id': t.user.id, 'username': t.user.username} for t in teachers]
    return JsonResponse({'users': users_data})

@login_required
def reply_message(request, message_id):
    original_msg = get_object_or_404(Message, id=message_id)

    if request.method == "POST":
        subject = request.POST.get("subject")
        body = request.POST.get("body")
        Message.objects.create(
            sender=request.user,
            recipient=original_msg.sender,
            subject=subject,
            body=body
        )
        return redirect('sent_messages')

    return render(request, "reply_message.html", {"original_msg": original_msg})


def shared_page(request):
    if request.user.is_superuser:
        back_url = reverse('admin_dashboard')
    else:
        back_url = reverse('teacher_dashboard')

    return render(request, 'shared_page.html', {
        'back_url': back_url
    })

@login_required
def class_list_view(request):
    # Decide where "Back" should go
    if request.user.is_superuser:
        back_url = reverse('admin_dashboard')
    else:
        back_url = reverse('teacher_dashboard')

    return render(request, 'class_list.html', {
        'classes': Class.objects.all(),
        'back_url': back_url,
    })




from django.db.models import Count, Avg


def admin_dashboard(request):
    # Modern AJAX detection
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = {
            "total_students": Student.objects.count(),
            "total_teachers": TeacherProfile.objects.count(),
            "total_subjects": Subject.objects.count(),
            "total_classes": Class.objects.count(),
            "total_departments": Department.objects.count(),
            "total_notices": Notice.objects.count(),
        }

        # Chart data
        results_qs = Result.objects.all()
        terms = Result.TERM_CHOICES
        test_types = Result.TEST_CHOICES

        results_data = {"terms": [t[1] for t in terms], "test_types": [tt[1] for tt in test_types], "data": {}}
        for test_code, test_name in test_types:
            results_data["data"][test_name] = [
                round(results_qs.filter(test_type=test_code, term=term_code).aggregate(avg=Avg('marks'))['avg'] or 0, 1)
                for term_code, term_name in terms
            ]

        data["results"] = results_data
        return JsonResponse(data)

    # Normal page load
    return render(request, "admin_dashboard.html")

#MATERIAL DOWNLOAD
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import TeacherMaterial, StudentMaterial

# ================= LEARNING MATERIALS SELECTION =================
from django.contrib.auth.decorators import login_required

# Teacher login page
def teacher_material_login(request):
    next_url = request.GET.get('next', reverse('teacher_materials'))  # default redirect
    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(next_url)
        else:
            error = "Invalid username or password."

    context = {
        'error': error,
        'next': next_url
    }
    return render(request, 'teacher_material_login.html', context)


# ================= Student Material Levels =================
STUDENT_LEVELS = [
    ('ECE', 'Early Childhood Education'),
    ('Lower Primary', 'Lower Primary'),
    ('Upper Primary', 'Upper Primary'),
    ('Junior', 'Junior Secondary'),
    ('Senior', 'Senior Secondary'),
]

def student_material_login(request):
    """
    Student logs in using exam number. If valid, redirect to student_materials page.
    """
    if request.method == 'POST':
        exam_no = request.POST.get('exam_no')

        # Check if student exists
        if Student.objects.filter(exam_no=exam_no).exists():
            request.session['exam_no'] = exam_no  # save session
            return redirect('student_materials')  # Redirect to the levels page
        else:
            messages.error(request, "Invalid exam number.")

    return render(request, 'student_material_login.html')

def student_materials(request):
    """
    Page to show all levels after student login.
    """
    exam_no = request.session.get('exam_no')
    if not exam_no:
        messages.error(request, "Please login first.")
        return redirect('student_material_login')

    # Pass only the level names for the template
    student_levels = [level[0] for level in STUDENT_LEVELS]

    return render(request, 'student_materials.html', {'student_levels': student_levels})

# Teacher materials page (after login)
@login_required
def teacher_materials(request):
    # Teacher categories
    categories = ['Syllabi', 'Schemes of Work', 'Lesson Plans', 'Modules', 'Templates', 'Past Papers', 'Books', 'Miscellaneous']

    context = {
        'categories': categories
    }
    return render(request, 'teacher_materials.html', context)


# ---------------- Learning Materials Page ----------------  # Ensure your Material model is imported

def learning_materials(request):
    # Teacher categories with corresponding icons
    teacher_categories = [
        'Syllabi', 'Schemes of Work', 'Lesson Plans', 'Modules',
        'Templates', 'Past Papers', 'Books', 'Miscellaneous'
    ]
    category_icons = {
        "Syllabi": "bi-journal-text",
        "Schemes of Work": "bi-layout-text-window-reverse",
        "Lesson Plans": "bi-pencil-square",
        "Modules": "bi-folder2",
        "Templates": "bi-file-earmark-text",
        "Past Papers": "bi-file-earmark-check",
        "Books": "bi-book",
        "Miscellaneous": "bi-file-earmark"
    }
    # Build a list of dicts for template
    categories_with_icons = [
        {'name': cat, 'icon': category_icons.get(cat, 'bi-file-earmark')} for cat in teacher_categories
    ]

    # Student levels with icons
    student_levels = ['ECE', 'Lower Primary', 'Upper Primary', 'Junior', 'Senior']
    level_icons = {
        'ECE': 'bi-emoji-smile',
        'Lower Primary': 'bi-1-circle',
        'Upper Primary': 'bi-2-circle',
        'Junior': 'bi-3-circle',
        'Senior': 'bi-4-circle'
    }
    levels_with_icons = [
        {'name': lvl, 'icon': level_icons.get(lvl, 'bi-book')} for lvl in student_levels
    ]

    # Get selected category or level from GET parameters
    selected_category = request.GET.get('category')
    selected_level = request.GET.get('level')

    # Filter materials
    selected_teacher_materials = TeacherMaterial.objects.none()
    selected_student_materials = StudentMaterial.objects.none()

    if selected_category:
        selected_teacher_materials = TeacherMaterial.objects.filter(category=selected_category)
    if selected_level:
        selected_student_materials = StudentMaterial.objects.filter(level=selected_level)

    context = {
        'categories': categories_with_icons,
        'student_levels': levels_with_icons,
        'selected_category': selected_category,
        'selected_level': selected_level,
        'selected_teacher_materials': selected_teacher_materials,
        'selected_student_materials': selected_student_materials,
    }

    return render(request, 'learning_materials.html', context)


#ADMIN MATERIAL UPDATE
from .forms import StudentMaterialForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import TeacherMaterialForm, StudentMaterialForm

# ---------------- Upload Teacher Material ----------------
@login_required
def upload_teacher_material(request):
    if request.method == 'POST':
        form = TeacherMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = request.user
            material.save()
            messages.success(request, "Teacher material uploaded successfully!")
            return redirect('upload_teacher_material')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = TeacherMaterialForm()

    return render(request, 'upload_teacher_material.html', {'form': form})


# ---------------- Upload Student Material ----------------
@login_required
def upload_student_material(request):
    if request.method == 'POST':
        form = StudentMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = request.user
            material.save()
            messages.success(request, "Student material uploaded successfully!")
            return redirect('upload_student_material')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = StudentMaterialForm()

    return render(request, 'upload_student_material.html', {'form': form})

#ADMIN MATERIAL UPLOAD DASHBARD
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import TeacherMaterialForm, StudentMaterialForm

# ---------------- Admin Upload Dashboard ----------------
@login_required
def upload_materials_dashboard(request):
    teacher_form = TeacherMaterialForm(prefix='teacher')
    student_form = StudentMaterialForm(prefix='student')

    if request.method == 'POST':
        if 'upload_teacher' in request.POST:
            teacher_form = TeacherMaterialForm(request.POST, request.FILES, prefix='teacher')
            if teacher_form.is_valid():
                material = teacher_form.save(commit=False)
                material.uploaded_by = request.user
                material.save()
                messages.success(request, "Teacher material uploaded successfully!")
                return redirect('upload_materials_dashboard')
            else:
                messages.error(request, "Please fix errors in the Teacher material form.")

        elif 'upload_student' in request.POST:
            student_form = StudentMaterialForm(request.POST, request.FILES, prefix='student')
            if student_form.is_valid():
                material = student_form.save(commit=False)
                material.uploaded_by = request.user
                material.save()
                messages.success(request, "Student material uploaded successfully!")
                return redirect('upload_materials_dashboard')
            else:
                messages.error(request, "Please fix errors in the Student material form.")

    return render(request, 'upload_materials_dashboard.html', {
        'teacher_form': teacher_form,
        'student_form': student_form,
    })

def materials_selection(request):
    # This page shows Teacher Materials and Student Materials buttons
    return render(request, 'materials_selection.html')

def teacher_materials_by_category(request, category):
    materials = TeacherMaterial.objects.filter(category=category)

    context = {
        'category': category,
        'materials': materials,
    }

    return render(request, 'teacher_materials_by_category.html', context)

def student_materials_by_level(request, level):
    """
    Page to show/download materials for a specific level.
    """
    exam_no = request.session.get('exam_no')
    if not exam_no:
        messages.error(request, "Please login first.")
        return redirect('student_material_login')

    # Get all materials for the selected level
    materials = StudentMaterial.objects.filter(level=level)

    return render(request, 'student_materials_by_level.html', {
        'level': level,
        'materials': materials
    })

from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from .models import Class, Student, Result


@login_required
def junior_analysis_select(request):
    # Fetch only senior classes
    senior_classes = Class.objects.filter(level='JUNIOR').order_by("numeric_name", "section")

    # Fetch distinct terms and tests from Result table
    terms = Result.objects.values_list("term", flat=True).distinct().order_by("term")
    tests = Result.objects.values_list("test_type", flat=True).distinct().order_by("test_type")
    subjects = Subject.objects.all().order_by("subject_name")

    context = {
        "classes": senior_classes,
        "terms": terms,
        "tests": tests,
        "subjects": subjects,
    }
    return render(request, "junior_analysis_select.html", context)

def junior_analysis_results(request):
    class_id = request.GET.get("class_id")
    term = request.GET.get("term")
    test_type = request.GET.get("test_type")
    subject_ids = request.GET.getlist("subject_ids")

    if not all([class_id, term, test_type, subject_ids]):
        messages.warning(request, "Please select all required fields.")
        return redirect("junior_analysis_select")

    selected_class = get_object_or_404(Class, id=class_id)
    selected_subjects = Subject.objects.filter(id__in=subject_ids)

    # 🔥 AUTO-DETECT YEAR (NO SUBJECT FILTER)
    year = (
        Result.objects.filter(
            student_class=selected_class,
            term=term,
            test_type=test_type
        )
        .values_list("year", flat=True)
        .distinct()
        .order_by("-year")
        .first()
    )

    if not year:
        messages.warning(
            request,
            "No results found for the selected class, term and test."
        )
        return redirect("junior_analysis_select")

    students_in_class = selected_class.students.all()

    grades = ["ONE", "TWO", "THREE", "FOUR"]
    gender_map = {"Female": "Girls", "Male": "Boys"}

    analysis = {}

    for subject in selected_subjects:
        subject_results = Result.objects.filter(
            student_class=selected_class,
            subject=subject,
            term=term,
            test_type=test_type,
            year=year
        )

        data = {
            "entrants": {"Girls": 0, "Boys": 0},
            "sat": {"Girls": 0, "Boys": 0},
            "absent": {"Girls": 0, "Boys": 0},
            "passed": {
                "Girls": {g: 0 for g in grades},
                "Boys": {g: 0 for g in grades},
            },
            "failed": {"Girls": 0, "Boys": 0},
            "pass_percentage": {"Girls": 0.0, "Boys": 0.0, "Total": 0.0},
        }

        for db_gender, label in gender_map.items():
            gender_students = students_in_class.filter(gender=db_gender)
            data["entrants"][label] = gender_students.count()

            g_results = subject_results.filter(student__gender=db_gender)
            data["sat"][label] = g_results.count()
            data["absent"][label] = data["entrants"][label] - data["sat"][label]

            data["failed"][label] = g_results.filter(marks__lt=40).count()

            data["passed"][label]["ONE"] = g_results.filter(marks__gte=75).count()
            data["passed"][label]["TWO"] = g_results.filter(marks__gte=60, marks__lt=75).count()
            data["passed"][label]["THREE"] = g_results.filter(marks__gte=50, marks__lt=60).count()
            data["passed"][label]["FOUR"] = g_results.filter(marks__gte=40, marks__lt=50).count()

            passed_total = sum(data["passed"][label].values())
            data["pass_percentage"][label] = (
                round((passed_total / data["sat"][label]) * 100, 2)
                if data["sat"][label] else 0
            )

        total_passed = sum(
            sum(data["passed"][g].values()) for g in ["Girls", "Boys"]
        )
        total_sat = data["sat"]["Girls"] + data["sat"]["Boys"]
        data["pass_percentage"]["Total"] = (
            round((total_passed / total_sat) * 100, 2)
            if total_sat else 0
        )

        analysis[subject.subject_name] = data

    context = {
        "analysis": analysis,
        "selected_class": selected_class,
        "selected_subjects": selected_subjects,
        "term": term,
        "test_type": test_type,
        "year": year,
        "grades": grades,
        "pass_keys": ["Girls", "Boys", "Total"],
    }

    return render(
        request,
        "ResultsApp/junior_analysis_results.html",
        context
    )

import openpyxl
from openpyxl.styles import Font, Alignment
from openpyxl import Workbook
from django.contrib import messages

def download_junior_analysis_excel(request):
    class_id = request.GET.get("class_id")
    term = request.GET.get("term")
    test_type = request.GET.get("test_type")
    subject_ids = request.GET.getlist("subject_ids")

    if not all([class_id, term, test_type, subject_ids]):
        messages.warning(request, "Please select all required fields.")
        return redirect("junior_analysis_select")

    selected_class = get_object_or_404(Class, id=class_id)
    selected_subjects = Subject.objects.filter(id__in=subject_ids)
    students_in_class = selected_class.students.all()

    # AUTO-DETECT YEAR
    year = (
        Result.objects.filter(
            student_class=selected_class,
            term=term,
            test_type=test_type
        )
        .values_list("year", flat=True)
        .distinct()
        .order_by("-year")
        .first()
    )

    if not year:
        messages.warning(
            request,
            "No results found for the selected class, term and test."
        )
        return redirect("junior_analysis_select")

    grades = ["ONE", "TWO", "THREE", "FOUR"]
    gender_map = {"Female": "Girls", "Male": "Boys"}

    # ===========================
    # Prepare Workbook
    # ===========================
    wb = Workbook()
    ws = wb.active
    ws_title = f"{selected_class} - {term} {test_type}"
    ws.title = ws_title[:31]  # Excel limit 31 chars

    # ===========================
    # Top-level headers
    # ===========================
    top_headers = [
        ("Subject", 1),
        ("Entrants", 2),
        ("Sat", 2),
        ("Absent", 2),
        ("Passed – Girls", len(grades)),
        ("Passed – Boys", len(grades)),
        ("Failed", 2),
        ("Pass %", 3),
    ]

    col = 1
    for header, span in top_headers:
        ws.merge_cells(start_row=1, start_column=col, end_row=1, end_column=col+span-1)
        cell = ws.cell(row=1, column=col, value=header)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.font = Font(bold=True)
        col += span

    # ===========================
    # Sub-headers row
    # ===========================
    subheaders = [
        "",  # Subject
        "Girls", "Boys",  # Entrants
        "Girls", "Boys",  # Sat
        "Girls", "Boys",  # Absent
    ] + grades + grades + ["Girls", "Boys", "Girls", "Boys", "Total"]  # Passed/Failed/Pass %

    for i, sh in enumerate(subheaders, start=1):
        cell = ws.cell(row=2, column=i, value=sh)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.font = Font(bold=True)

    ws.freeze_panes = "A3"

    # ===========================
    # Fill data
    # ===========================
    for subject in selected_subjects:
        subject_results = Result.objects.filter(
            student_class=selected_class,
            subject=subject,
            term=term,
            test_type=test_type,
            year=year
        )

        data = {
            "entrants": {"Girls": 0, "Boys": 0},
            "sat": {"Girls": 0, "Boys": 0},
            "absent": {"Girls": 0, "Boys": 0},
            "passed": {"Girls": {g: 0 for g in grades}, "Boys": {g: 0 for g in grades}},
            "failed": {"Girls": 0, "Boys": 0},
            "pass_percentage": {"Girls": 0.0, "Boys": 0.0, "Total": 0.0},
        }

        for db_gender, label in gender_map.items():
            gender_students = students_in_class.filter(gender=db_gender)
            data["entrants"][label] = gender_students.count()

            g_results = subject_results.filter(student__gender=db_gender)
            data["sat"][label] = g_results.count()
            data["absent"][label] = data["entrants"][label] - data["sat"][label]

            data["failed"][label] = g_results.filter(marks__lt=40).count()

            data["passed"][label]["ONE"] = g_results.filter(marks__gte=75).count()
            data["passed"][label]["TWO"] = g_results.filter(marks__gte=60, marks__lt=75).count()
            data["passed"][label]["THREE"] = g_results.filter(marks__gte=50, marks__lt=60).count()
            data["passed"][label]["FOUR"] = g_results.filter(marks__gte=40, marks__lt=50).count()

            passed_total = sum(data["passed"][label].values())
            data["pass_percentage"][label] = round((passed_total / data["sat"][label] * 100), 2) if data["sat"][label] else 0

        total_passed = sum(sum(data["passed"][g].values()) for g in ["Girls", "Boys"])
        total_sat = data["sat"]["Girls"] + data["sat"]["Boys"]
        data["pass_percentage"]["Total"] = round((total_passed / total_sat) * 100, 2) if total_sat else 0

        # Row values
        row = [
            subject.subject_name,
            data["entrants"]["Girls"], data["entrants"]["Boys"],
            data["sat"]["Girls"], data["sat"]["Boys"],
            data["absent"]["Girls"], data["absent"]["Boys"],
        ]
        row += [data["passed"]["Girls"][g] for g in grades]
        row += [data["passed"]["Boys"][g] for g in grades]
        row += [
            data["failed"]["Girls"], data["failed"]["Boys"],
            data["pass_percentage"]["Girls"], data["pass_percentage"]["Boys"], data["pass_percentage"]["Total"],
        ]
        ws.append(row)

    # ===========================
    # Serve Excel
    # ===========================
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{selected_class}_{term}_{test_type}_Junior_Analysis.xlsx"'
    wb.save(response)
    return response

def download_senior_analysis_excel(request):
    class_id = request.GET.get("class_id")
    term = request.GET.get("term")
    test_type = request.GET.get("test_type")
    subject_ids = request.GET.getlist("subject_ids")

    if not all([class_id, term, test_type]) or not subject_ids:
        messages.warning(request, "Missing parameters for Excel download.")
        return redirect("senior_analysis_select")

    selected_class = get_object_or_404(Class, id=class_id)
    subjects = Subject.objects.filter(id__in=subject_ids)
    students = selected_class.students.all()
    grades = ["ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT"]
    gender_map = {"Female": "Girls", "Male": "Boys"}

    year = (
        Result.objects.filter(student_class=selected_class, term=term, test_type=test_type)
        .values_list("year", flat=True)
        .order_by("-year")
        .first()
    )

    wb = Workbook()
    ws = wb.active
    title = f"{selected_class} - {term} {test_type}"
    ws.title = title[:31]  # Limit to 31 characters


    # ===========================
    # Header Row 1 (Top-level)
    # ===========================
    top_headers = [
        ("Subject", 1),
        ("Entrants", 2),
        ("Sat", 2),
        ("Absent", 2),
        ("Grades Girls", 8),
        ("Grades Boys", 8),
        ("Pass % 1-6", 3),
        ("Pass % 1-8", 3),
        ("Overall %", 1)
    ]

    col = 1
    for header, span in top_headers:
        ws.merge_cells(start_row=1, start_column=col, end_row=1, end_column=col+span-1)
        cell = ws.cell(row=1, column=col, value=header)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.font = Font(bold=True)
        col += span

    # ===========================
    # Header Row 2 (Sub-headers)
    # ===========================
    subheaders = [
        "",  # Subject
        "Girls", "Boys",  # Entrants
        "Girls", "Boys",  # Sat
        "Girls", "Boys",  # Absent
    ] + [str(i) for i in range(1, 9)] + [str(i) for i in range(1, 9)] + \
        ["Girls", "Boys", "Total"] + ["Girls", "Boys", "Total"] + [""]  # Overall %

    for i, sh in enumerate(subheaders, start=1):
        cell = ws.cell(row=2, column=i, value=sh)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.font = Font(bold=True)

    ws.freeze_panes = "A3"

    # ===========================
    # Fill Data Rows
    # ===========================
    for subject in subjects:
        subject_data = {
            "entrants": {"Girls": 0, "Boys": 0},
            "sat": {"Girls": 0, "Boys": 0},
            "absent": {"Girls": 0, "Boys": 0},
            "passed": {g: {gr: 0 for gr in grades} for g in ["Girls", "Boys"]},
            "pass_percentage_1_6": {"Girls": 0, "Boys": 0, "Total": 0},
            "pass_percentage_1_8": {"Girls": 0, "Boys": 0, "Total": 0},
            "overall_percentage": 0,
        }

        results = Result.objects.filter(
            student_class=selected_class, subject=subject, term=term, test_type=test_type, year=year
        )

        for db_gender, label in gender_map.items():
            g_students = students.filter(gender=db_gender)
            g_results = results.filter(student__gender=db_gender)

            subject_data["entrants"][label] = g_students.count()
            subject_data["sat"][label] = g_results.count()
            subject_data["absent"][label] = g_students.count() - g_results.count()

            # Fill grades ONE → EIGHT
            subject_data["passed"][label]["ONE"] = g_results.filter(marks__gte=75).count()
            subject_data["passed"][label]["TWO"] = g_results.filter(marks__gte=65, marks__lt=75).count()
            subject_data["passed"][label]["THREE"] = g_results.filter(marks__gte=55, marks__lt=65).count()
            subject_data["passed"][label]["FOUR"] = g_results.filter(marks__gte=50, marks__lt=55).count()
            subject_data["passed"][label]["FIVE"] = g_results.filter(marks__gte=45, marks__lt=50).count()
            subject_data["passed"][label]["SIX"] = g_results.filter(marks__gte=40, marks__lt=45).count()
            subject_data["passed"][label]["SEVEN"] = g_results.filter(marks__gte=85, marks__lt=90).count()
            subject_data["passed"][label]["EIGHT"] = g_results.filter(marks__gte=90).count()

            total_1_6 = sum(subject_data["passed"][label][g] for g in grades[:6])
            total_1_8 = sum(subject_data["passed"][label][g] for g in grades)
            subject_data["pass_percentage_1_6"][label] = round((total_1_6 / g_results.count() * 100), 2) if g_results.count() else 0
            subject_data["pass_percentage_1_8"][label] = round((total_1_8 / g_results.count() * 100), 2) if g_results.count() else 0

        total_sat = subject_data["sat"]["Girls"] + subject_data["sat"]["Boys"]
        total_1_6 = sum(subject_data["passed"][g][gr] for g in ["Girls", "Boys"] for gr in grades[:6])
        total_1_8 = sum(subject_data["passed"][g][gr] for g in ["Girls", "Boys"] for gr in grades)
        subject_data["pass_percentage_1_6"]["Total"] = round((total_1_6 / total_sat * 100), 2) if total_sat else 0
        subject_data["pass_percentage_1_8"]["Total"] = round((total_1_8 / total_sat * 100), 2) if total_sat else 0
        subject_data["overall_percentage"] = subject_data["pass_percentage_1_8"]["Total"]

        # Create row
        row = [
            subject.subject_name,
            subject_data["entrants"]["Girls"], subject_data["entrants"]["Boys"],
            subject_data["sat"]["Girls"], subject_data["sat"]["Boys"],
            subject_data["absent"]["Girls"], subject_data["absent"]["Boys"],
        ]
        row += [subject_data["passed"]["Girls"][g] for g in grades]
        row += [subject_data["passed"]["Boys"][g] for g in grades]
        row += [
            subject_data["pass_percentage_1_6"]["Girls"],
            subject_data["pass_percentage_1_6"]["Boys"],
            subject_data["pass_percentage_1_6"]["Total"],
            subject_data["pass_percentage_1_8"]["Girls"],
            subject_data["pass_percentage_1_8"]["Boys"],
            subject_data["pass_percentage_1_8"]["Total"],
            subject_data["overall_percentage"],
        ]
        ws.append(row)

    # ===========================
    # Serve as Excel response
    # ===========================
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{selected_class}_{term}_{test_type}_Analysis.xlsx"'
    wb.save(response)
    return response

def senior_analysis_results(request):
    class_id = request.GET.get("class_id")
    term = request.GET.get("term")
    test_type = request.GET.get("test_type")
    subject_ids = request.GET.getlist("subject_ids")

    if not all([class_id, term, test_type, subject_ids]):
        messages.warning(request, "Please select all required fields.")
        return redirect("senior_analysis_select")

    selected_class = get_object_or_404(Class, id=class_id)
    selected_subjects = Subject.objects.filter(id__in=subject_ids)
    students = selected_class.students.all()
    grades = ["ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT"]
    gender_map = {"Female": "Girls", "Male": "Boys"}

    # Get latest year
    year = (
        Result.objects.filter(
            student_class=selected_class,
            term=term,
            test_type=test_type
        )
        .values_list("year", flat=True)
        .order_by("-year")
        .first()
    )

    data = {}

    for subject in selected_subjects:
        subject_data = {
            "entrants": {"Girls": 0, "Boys": 0},
            "sat": {"Girls": 0, "Boys": 0},
            "absent": {"Girls": 0, "Boys": 0},
            "passed": {g: {gr: 0 for gr in grades} for g in ["Girls", "Boys"]},
            "pass_percentage_1_6": {"Girls": 0, "Boys": 0, "Total": 0},
            "pass_percentage_1_8": {"Girls": 0, "Boys": 0, "Total": 0},
            "overall_percentage": 0,
        }

        results = Result.objects.filter(
            student_class=selected_class,
            subject=subject,
            term=term,
            test_type=test_type,
            year=year
        )

        for db_gender, label in gender_map.items():
            g_students = students.filter(gender=db_gender)
            g_results = results.filter(student__gender=db_gender)

            subject_data["entrants"][label] = g_students.count()
            subject_data["sat"][label] = g_results.count()
            subject_data["absent"][label] = g_students.count() - g_results.count()

            # Count grades
            subject_data["passed"][label]["ONE"] = g_results.filter(marks__gte=75).count()
            subject_data["passed"][label]["TWO"] = g_results.filter(marks__gte=65, marks__lt=75).count()
            subject_data["passed"][label]["THREE"] = g_results.filter(marks__gte=55, marks__lt=65).count()
            subject_data["passed"][label]["FOUR"] = g_results.filter(marks__gte=50, marks__lt=55).count()
            subject_data["passed"][label]["FIVE"] = g_results.filter(marks__gte=45, marks__lt=50).count()
            subject_data["passed"][label]["SIX"] = g_results.filter(marks__gte=40, marks__lt=45).count()
            subject_data["passed"][label]["SEVEN"] = g_results.filter(marks__gte=85, marks__lt=90).count()
            subject_data["passed"][label]["EIGHT"] = g_results.filter(marks__gte=90).count()

            # Pass percentages
            total_1_6 = sum(subject_data["passed"][label][g] for g in grades[:6])
            total_1_8 = sum(subject_data["passed"][label][g] for g in grades)
            subject_data["pass_percentage_1_6"][label] = round((total_1_6 / g_results.count() * 100), 2) if g_results.count() else 0
            subject_data["pass_percentage_1_8"][label] = round((total_1_8 / g_results.count() * 100), 2) if g_results.count() else 0

        # Totals
        total_sat = subject_data["sat"]["Girls"] + subject_data["sat"]["Boys"]
        total_1_6 = sum(subject_data["passed"][g][gr] for g in ["Girls", "Boys"] for gr in grades[:6])
        total_1_8 = sum(subject_data["passed"][g][gr] for g in ["Girls", "Boys"] for gr in grades)
        subject_data["pass_percentage_1_6"]["Total"] = round((total_1_6 / total_sat * 100), 2) if total_sat else 0
        subject_data["pass_percentage_1_8"]["Total"] = round((total_1_8 / total_sat * 100), 2) if total_sat else 0
        subject_data["overall_percentage"] = subject_data["pass_percentage_1_8"]["Total"]

        data[subject.subject_name] = subject_data

    context = {
        "data": data,
        "selected_class": selected_class,
        "selected_subjects": selected_subjects,
        "subject_ids": [s.id for s in selected_subjects],  # must pass for download
        "term": term,
        "test_type": test_type,
        "year": year,
        "grades": grades,
    }

    return render(request, "ResultsApp/senior_analysis_results.html", context)


# views.py
from django.shortcuts import render, redirect
from .models import Class, Subject  # Adjust imports to your models

@login_required
def senior_analysis_select(request):
    # Fetch only senior classes
    senior_classes = Class.objects.filter(level='SENIOR').order_by("numeric_name", "section")

    # Fetch distinct terms and tests from Result table
    terms = Result.objects.values_list("term", flat=True).distinct().order_by("term")
    tests = Result.objects.values_list("test_type", flat=True).distinct().order_by("test_type")
    subjects = Subject.objects.all().order_by("subject_name")

    context = {
        "classes": senior_classes,
        "terms": terms,
        "tests": tests,
        "subjects": subjects,
    }
    return render(request, "senior_analysis_select.html", context)

from django.shortcuts import render
from .ai_services import generate_lesson_plan

def lesson_plan_view(request):
    if request.method == "POST":
        data = request.POST

        prompt = f"""
        Generate a professional Zambian secondary school lesson plan.

        Sections:
        - Introduction
        - Development
        - Conclusion
        - Homework
        - Evaluation

        Include:
        - Teacher Activities
        - Learner Activities
        - Content
        - Methods

        DETAILS:
        Teacher: {data.get('teacher_name', '')}
        Subject: {data.get('subject', '')}
        Class: {data.get('class_name', '')}
        Date: {data.get('date', '')}
        Topic: {data.get('topic', '')}
        Subtopic: {data.get('subtopic', '')}
        Duration: {data.get('duration', '')}
        Time: {data.get('time', '')}
        """

        lesson = generate_lesson_plan(prompt)

        request.session["lesson"] = lesson

        return render(request, "lesson_result.html", {"lesson": lesson})

    return render(request, "lesson_plan_form.html")

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from weasyprint import HTML
from docx import Document
from django.http import HttpResponse
from .models import RecordOfWork
import zipfile
from io import BytesIO


@login_required
def records_of_work(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        subject = request.POST.get('subject')
        year = request.POST.get('year')
        term = request.POST.get('term')
        grade = request.POST.get('grade')

        week = request.POST.getlist('week[]')
        work_done = request.POST.getlist('work_done[]')
        work_not_done = request.POST.getlist('work_not_done[]')

        # ✅ FIXED FIELD NAMES (must match your form)
        teacher_comments = request.POST.getlist('teacher_comments[]')
        hod_remarks = request.POST.getlist('hod_remarks[]')

        # ✅ Save records safely
        for w, wd, wnd, c, r in zip(
            week, work_done, work_not_done, teacher_comments, hod_remarks
        ):
            if w:  # prevent empty rows
                RecordOfWork.objects.create(
                    teacher=request.user,
                    subject=subject,
                    year=year,
                    term=term,
                    grade=grade,
                    week=w,
                    work_done=wd,
                    work_not_done=wnd,
                    teacher_comments=c,
                    hod_remarks=r
                )

        # ✅ HANDLE DOWNLOADS (correct indentation)
        if action == 'pdf':
            return generate_pdf_zip(
                request.user, subject, year, term, grade,
                week, work_done, work_not_done,
                teacher_comments, hod_remarks
            )

        elif action == 'word':
            return generate_word_zip(
                request.user, subject, year, term, grade,
                week, work_done, work_not_done,
                teacher_comments, hod_remarks
            )

        return redirect('records_of_work')

    return render(request, 'records_of_work.html')

def schemes_of_work_view(request):
    return HttpResponse("Schemes of Work Page")

from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
from .models import RecordOfWork

def generate_pdf_zip(user, subject, year, term, grade,
                     week, work_done, work_not_done,
                     teacher_comments, hod_remarks):

    buffer = BytesIO()
    zip_file = zipfile.ZipFile(buffer, 'w')

    for i, (w, wd, wnd, c, r) in enumerate(zip(
        week, work_done, work_not_done, teacher_comments, hod_remarks
    )):

        html = render_to_string('pdf_template.html', {
            'records': [(w, wd, wnd, c, r)],
            'teacher': user,
            'subject': subject,
            'year': year,
            'term': term,
            'grade': grade,
        })

        pdf_file = BytesIO()
        HTML(string=html).write_pdf(pdf_file)

        zip_file.writestr(f"week_{w}.pdf", pdf_file.getvalue())

    zip_file.close()

    response = HttpResponse(buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="records_of_work.zip"'

    return response

import zipfile
from io import BytesIO
from docx import Document
from django.http import HttpResponse

def generate_word_zip(user, subject, year, term, grade,
                      week, work_done, work_not_done,
                      teacher_comments, hod_remarks):

    buffer = BytesIO()
    zip_file = zipfile.ZipFile(buffer, 'w')

    for i in range(len(week)):
        document = Document()

        # Header
        document.add_paragraph('MINISTRY OF EDUCATION').alignment = 1
        document.add_paragraph('MUYOMBE DAY SECONDARY SCHOOL').alignment = 1
        document.add_paragraph('RECORD OF WORK').alignment = 1

        # Info
        document.add_paragraph(
            f"Teacher: {user}    Subject: {subject}    Year: {year}"
        )
        document.add_paragraph(
            f"Term: {term}    Grade: {grade}"
        )

        # Table
        table = document.add_table(rows=2, cols=5)

        headers = ["Week", "Work Done", "Work Not Done", "Teacher's Comments", "H.O.D Remarks"]
        for j, h in enumerate(headers):
            table.rows[0].cells[j].text = h

        table.rows[1].cells[0].text = week[i]
        table.rows[1].cells[1].text = work_done[i]
        table.rows[1].cells[2].text = work_not_done[i]
        table.rows[1].cells[3].text = teacher_comments[i]
        table.rows[1].cells[4].text = hod_remarks[i]

        # Save each doc in memory
        doc_buffer = BytesIO()
        document.save(doc_buffer)

        zip_file.writestr(f"week_{week[i]}.docx", doc_buffer.getvalue())

    zip_file.close()

    response = HttpResponse(buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=records_of_work.zip'

    return response



from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Student  # make sure you have this model


def student_login(request):
    if request.method == "POST":
        exam_no = request.POST.get("exam_no")

        # check if student exists
        student = Student.objects.filter(exam_no=exam_no).first()

        if student:
            # store session
            request.session['exam_no'] = student.exam_no
            request.session['student_id'] = student.id

            return redirect("student_dashboard")
        else:
            messages.error(request, "Invalid Exam Number")

    return render(request, "student_login.html")

from .models import Class, Result

def student_dashboard(request):
    student_id = request.session.get('student_id')

    if not student_id:
        return redirect('student_login')

    student = Student.objects.select_related('student_class').get(id=student_id)

    return render(request, 'student_dashboard.html', {
        'exam_no': student.exam_no,
        'student_class': student.student_class,
        'term_choices': Result.TERM_CHOICES,
        'test_choices': Result.TEST_CHOICES,
    })

from django.utils.timezone import now
from django.shortcuts import redirect
from django.templatetags.static import static
from django.http import HttpResponse
from django.template.loader import render_to_string
from io import BytesIO
from weasyprint import HTML
from django.conf import settings
import os


# ✅ Handles static + media files
def weasyprint_url_fetcher(url):
    if url.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, url.replace(settings.MEDIA_URL, ""))
        return {'file_obj': open(path, 'rb')}

    if url.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, url.replace(settings.STATIC_URL, ""))
        return {'file_obj': open(path, 'rb')}

    return {}


def results_form(request):
    if request.method == "POST":

        student_id = request.session.get('student_id')
        if not student_id:
            return redirect('student_login')

        student = Student.objects.get(id=student_id)
        cls = student.student_class

        term = request.POST.get("term")
        test_type = request.POST.get("test_type")

        results_qs = Result.objects.filter(
            student=student,
            term=term,
            test_type=test_type
        ).select_related("subject")

        results_data = []

        for res in results_qs:
            if res.is_absent:
                mark_display = "A"
                grade = "-"
                comment = "Absent"
            else:
                mark_display = res.marks
                grade, comment = get_grade_comment(cls.level, res.marks)

            results_data.append({
                "subject": res.subject.subject_name if res.subject else "N/A",
                "mark": mark_display,
                "grade": grade,
                "comment": comment,
            })

        teacher_comment, head_comment = generate_teacher_head_comments(results_data)

        report_date = now().strftime("%d %B %Y")
        generated_stamp = generate_stamp_with_date(report_date)

        # ===============================
        # HTML
        # ===============================
        html = render_to_string("results_form.html", {
            "student": student,
            "cls": cls,
            "term": term,
            "test_type": test_type,
            "results": results_data,
            "teacher_comment": teacher_comment,
            "head_comment": head_comment,
            "report_date": report_date,
            "head_signature": static("images/head_signature.png"),
            "head_stamp": generated_stamp,
        })

        # ===============================
        # PDF (WEASYPRINT)
        # ===============================
        pdf_file = BytesIO()

        HTML(
            string=html,
            base_url=request.build_absolute_uri("/")  # VERY IMPORTANT
        ).write_pdf(
            target=pdf_file,
            url_fetcher=weasyprint_url_fetcher
        )

        response = HttpResponse(pdf_file.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{student.first_name}_Report.pdf"'

        return response

    return redirect("student_dashboard")

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.templatetags.static import static
from io import BytesIO
from weasyprint import HTML
from django.conf import settings
import os


# ✅ Handles static + media for WeasyPrint
def weasyprint_url_fetcher(url):
    if url.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, url.replace(settings.MEDIA_URL, ""))
        return {'file_obj': open(path, 'rb')}

    if url.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, url.replace(settings.STATIC_URL, ""))
        return {'file_obj': open(path, 'rb')}

    return {}


def generate_student_report(request):

    if request.method != "POST":
        return HttpResponse("Invalid request method", status=405)

    # ===============================
    # SESSION ONLY
    # ===============================
    student_id = request.session.get("student_id")

    if not student_id:
        return redirect("student_login")

    term = request.POST.get("term")
    test_type = request.POST.get("test_type")

    if not term or not test_type:
        return HttpResponse("Missing term or test type", status=400)

    student = get_object_or_404(Student, id=student_id)
    cls = student.student_class

    # ===============================
    # RESULTS
    # ===============================
    results_qs = Result.objects.filter(
        student=student,
        term=term,
        test_type=test_type
    ).select_related("subject")

    results_data = []

    for res in results_qs:
        if res.is_absent:
            mark_display = "A"
            grade = "-"
            comment = "Absent"
        else:
            mark_display = res.marks
            grade, comment = get_grade_comment(cls.level, res.marks)

        results_data.append({
            "subject": res.subject.subject_name if res.subject else "N/A",
            "mark": mark_display,
            "grade": grade,
            "comment": comment,
        })

    teacher_comment, head_comment = generate_teacher_head_comments(results_data)

    report_date = now().strftime("%d %B %Y")
    generated_stamp = generate_stamp_with_date(report_date)

    # ===============================
    # HTML RENDER
    # ===============================
    html = render_to_string("ecz_report_form.html", {
        "student": student,
        "cls": cls,
        "term": term,
        "test_type": test_type,
        "results": results_data,
        "teacher_comment": teacher_comment,
        "head_comment": head_comment,
        "report_date": report_date,
        "head_signature": static("images/head_signature.png"),
        "head_stamp": generated_stamp,
    })

    # ===============================
    # PDF GENERATION (WEASYPRINT)
    # ===============================
    pdf_file = BytesIO()

    HTML(
        string=html,
        base_url=request.build_absolute_uri("/")  # VERY IMPORTANT
    ).write_pdf(
        target=pdf_file,
        url_fetcher=weasyprint_url_fetcher
    )

    response = HttpResponse(pdf_file.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{student.exam_no}_report.pdf"'

    return response