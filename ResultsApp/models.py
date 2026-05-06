from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords 
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

class Class(models.Model):
     LEVEL_CHOICES = (
        ('ECE', 'ECE'),
        ('LOWER_PRIMARY', 'Lower Primary'),
        ('UPPER_PRIMARY', 'Upper Primary'),
        ('JUNIOR', 'Junior'),
        ('SENIOR', 'Senior'),
    )
     class_name = models.CharField(max_length=100)
     numeric_name = models.IntegerField()
     level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES
    )
     section = models.CharField(max_length=10)
     session = models.PositiveIntegerField(
        validators=[
            MinValueValidator(2022),
            MaxValueValidator(2030),
        ]
    )
     year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(2022),
            MaxValueValidator(2030),
        ]
    )
     creation_date = models.DateTimeField(auto_now_add=True)
     updation_date = models.DateTimeField(auto_now=True)

     def __str__(self):
        return f"{self.class_name} {self.numeric_name} {self.section} {self.session} {self.year}"
    
class Student(models.Model):
    GENDER_CHOICES = (
        ('Male','Male'),
        ('Female','Female'),
    )
    DISABILITY_CHOICES = (
        ('none', 'None'),
        ('visual', 'Visual Impairment'),
        ('hearing', 'Hearing Impairment'),
        ('physical', 'Physical Disability'),
        ('Intellectual', 'Intellectual Disability'),
        ('multiple', 'Multiple Disability'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    student_class = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        related_name='students'  # ✅ Add this line
    )
    photo = models.ImageField(upload_to='student_photos/', null=True, blank=True)
    exam_no = models.CharField(max_length=12, unique=True)
    phone_no = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    dob = models.CharField(max_length=20)
    address = models.CharField(max_length=50)
    parent_name = models.CharField(max_length=30)
    disability = models.CharField(max_length=20, choices=DISABILITY_CHOICES, default='none')
    registration_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class SubjectCombination(models.Model):
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    status = models.IntegerField(default=1)
    creation_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student_class} - {self.subject}"

class Result(models.Model):
    TEST_CHOICES = (
        ('TEST1', 'Test 1'),
        ('TEST2', 'Test 2'),
        ('EOT', 'End of Term'),
    )

    TERM_CHOICES = (
        ('TERM1', 'Term 1'),
        ('TERM2', 'Term 2'),
        ('TERM3', 'Term 3'),
    )

    student = models.ForeignKey(
        'Student',
        on_delete=models.CASCADE,
        related_name='results'  # <-- important!
    )
    student_class = models.ForeignKey('Class', on_delete=models.SET_NULL, null=True)
    subject = models.ForeignKey('Subject', on_delete=models.SET_NULL, null=True)

    test_type = models.CharField(max_length=10, choices=TEST_CHOICES)
    term = models.CharField(max_length=10, choices=TERM_CHOICES)
    year = models.IntegerField()
    marks = models.IntegerField(null=True, blank=True)
    posting_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)
    is_absent = models.BooleanField(default=False)

    # Simple History
    history = HistoricalRecords(user_model=User)

from django.db import models

class Notice(models.Model):
    title = models.CharField(max_length=200)
    details = models.TextField()
    link = models.URLField(blank=True, null=True)
    attachment = models.FileField(upload_to='notices/files/', blank=True, null=True)
    image = models.ImageField(upload_to='notices/images/', blank=True, null=True)
    posting_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title



class Department(models.Model):
    department_name = models.CharField(max_length=100, unique=True)
    department_code = models.CharField(max_length=10, unique=True)
    hod = models.CharField(max_length=50)
    no_of_teachers = models.IntegerField(default=0)
    creation_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.department_name


# Choice constants
GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
]

MARITAL_STATUS_CHOICES = [
    ('Single', 'Single'),
    ('Married', 'Married'),
    ('Divorced', 'Divorced'),
    ('Widowed', 'Widowed'),
]

NATIONALITY_CHOICES = [
    ('ZAMBIAN', 'Zambian'),
    ('FOREIGN', 'Foreign'),
]

DISABILITY_CHOICES = [
    ('none', 'None'),
    ('physical', 'Physical'),
    ('visual', 'Visual'),
    ('hearing', 'Hearing'),
]

CONFIRMED_CHOICES = [
    ('Yes', 'Yes'),
    ('No', 'No'),
]

NEXT_OF_KIN_RELATIONSHIP_CHOICES = [
    ('PARENT', 'Parent'),
    ('SPOUSE', 'Spouse'),
    ('SIBLING', 'Sibling'),
    ('CHILD', 'Child'),
    ('GUARDIAN', 'Guardian'),
    ('OTHER', 'Other'),
]


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Personal info
    surname = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    other_names = models.CharField(max_length=50, blank=True, null=True)

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES)
    nationality = models.CharField(max_length=20, choices=NATIONALITY_CHOICES)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_no = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    disability = models.CharField(max_length=20, choices=DISABILITY_CHOICES, default='none')

    # Departments
    department1 = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_teachers'
    )
    department2 = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='secondary_teachers'
    )

    # Academic / Professional info
    academic_qualification = models.CharField(max_length=100, blank=True, null=True)
    professional_qualification = models.CharField(max_length=100, blank=True, null=True)
    minor = models.CharField(max_length=100, blank=True, null=True)
    major = models.CharField(max_length=100, blank=True, null=True)
    college_university = models.CharField(max_length=150, blank=True, null=True)
    year_of_graduation = models.IntegerField(blank=True, null=True)

    # Employment / Position info
    date_first_app = models.DateField(blank=True, null=True)
    date_current_app = models.DateField(blank=True, null=True)
    date_of_retirement = models.DateField(blank=True, null=True)
    position_first_app = models.CharField(max_length=100, blank=True, null=True)
    substantive_position = models.CharField(max_length=100, blank=True, null=True)
    current_position = models.CharField(max_length=100, blank=True, null=True)
    confirmed = models.CharField(max_length=3, choices=CONFIRMED_CHOICES, default='No')

    # Salary / Pay info
    pay_point = models.CharField(max_length=50, blank=True, null=True)
    district_of_pay_point = models.CharField(max_length=100, blank=True, null=True)
    salary_scale = models.CharField(max_length=50, blank=True, null=True)

    # Next of Kin info
    next_of_kin_name = models.CharField(max_length=100, blank=True, null=True)
    next_of_kin_phone = models.CharField(max_length=15, blank=True, null=True)
    next_of_kin_relationship = models.CharField(max_length=20, choices=NEXT_OF_KIN_RELATIONSHIP_CHOICES, blank=True, null=True)
    next_of_kin_district = models.CharField(max_length=100, blank=True, null=True)

    # Banking info
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    branch_name = models.CharField(max_length=100, blank=True, null=True)

    # Location info
    current_station = models.CharField(max_length=150, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    distance_from_DEBs = models.FloatField(blank=True, null=True, help_text="Distance in km from DEB office")

    # IDs
    NRC_No = models.CharField(max_length=50, blank=True, null=True)
    TCZ_No = models.CharField(max_length=50, blank=True, null=True)
    TS_No = models.CharField(max_length=50, blank=True, null=True)
    Employ_No = models.CharField(max_length=50, blank=True, null=True)

    # Photo
    photo = models.ImageField(upload_to='teachers/', blank=True, null=True)

    # Many-to-many: classes and subjects
    classes = models.ManyToManyField('Class', blank=True)
    subjects = models.ManyToManyField('Subject', blank=True)

    def __str__(self):
        return f"{self.surname} {self.first_name} {self.other_names or ''}"

class Subject(models.Model):
    subject_name = models.CharField(max_length=100)
    subject_code = models.CharField(max_length=10)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject_name} {self.subject_code} ({self.department})"
    
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver  
@receiver([post_save, post_delete], sender=TeacherProfile)
def update_teacher_count(sender, instance, **kwargs):
    # Use both departments
    departments = [instance.department1, instance.department2]
    for dept_name in departments:
        if dept_name:
            dept_obj = Department.objects.filter(department_name=dept_name).first()
            if dept_obj:
                dept_obj.no_of_teachers = TeacherProfile.objects.filter(
                    models.Q(department1=dept_name) | models.Q(department2=dept_name)
                ).count()
                dept_obj.save()
                
class GradingSystem(models.Model):
    class_level = models.CharField(max_length=20, unique=True)

class Grade(models.Model):
    grading_system = models.ForeignKey(
        GradingSystem,
        related_name="grades",
        on_delete=models.CASCADE
    )
    min_mark = models.IntegerField()
    grade = models.CharField(max_length=5)
    comment = models.CharField(max_length=100)

# Messages between teachers/admins
class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} → {self.recipient}: {self.subject}"

# Notifications (alerts for teachers)
class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True, null=True)  # optional link
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} - {self.message[:20]}"

from django.db import models
from django.contrib.auth.models import User

# Categories for teacher materials
from django.db import models
from django.contrib.auth.models import User

# ================= Teacher Material Categories =================
TEACHER_CATEGORIES = [
    ('Syllabi', 'Syllabi'),
    ('Schemes of Work', 'Schemes of Work'),
    ('Lesson Plans', 'Lesson Plans'),
    ('Modules', 'Modules'),
    ('Templates', 'Templates'),
    ('Past Papers', 'Past Papers'),
    ('Books', 'Books'),
    ('Miscellaneous', 'Miscellaneous'),
]

# ================= Student Material Levels =================
STUDENT_LEVELS = [
    ('ECE', 'Early Childhood Education'),
    ('Lower Primary', 'Lower Primary'),
    ('Upper Primary', 'Upper Primary'),
    ('Junior', 'Junior Secondary'),
    ('Senior', 'Senior Secondary'),
]

# ================= Teacher Material Model =================
class TeacherMaterial(models.Model):
    """
    Model for storing teacher learning materials.
    Files are categorized (e.g., Syllabi, Lesson Plans, Modules).
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=TEACHER_CATEGORIES)
    file = models.FileField(upload_to='teacher_materials/')
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Teacher Material"
        verbose_name_plural = "Teacher Materials"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} ({self.category})"


# ================= Student Material Model =================
class StudentMaterial(models.Model):
    """
    Model for storing student learning materials.
    Files are organized by student levels (e.g., Junior, Senior, ECE).
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    level = models.CharField(max_length=50, choices=STUDENT_LEVELS)
    file = models.FileField(upload_to='student_materials/')
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Student Material"
        verbose_name_plural = "Student Materials"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} ({self.level})"

from django.db import models

class LearningMaterial(models.Model):
    CLASS_LEVELS = (
        ('ECE', 'ECE'),
        ('LOWER_PRIMARY', 'Lower Primary'),
        ('UPPER_PRIMARY', 'Upper Primary'),
        ('JUNIOR', 'Junior'),
        ('SENIOR', 'Senior'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    material_file = models.FileField(upload_to='learning_materials/')
    class_level = models.CharField(max_length=20, choices=CLASS_LEVELS)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.class_level})"

class RecordOfWork(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    year = models.CharField(max_length=20)
    term = models.CharField(max_length=20)
    grade = models.CharField(max_length=20)

    week = models.CharField(max_length=10)
    work_done = models.TextField()
    work_not_done = models.TextField(blank=True)
    teacher_comments = models.TextField(blank=True)
    hod_remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - Week {self.week}"
    
class TeacherAssignment(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    assigned_class = models.ForeignKey(Class, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('teacher', 'subject', 'assigned_class')

    def __str__(self):
        return f"{self.teacher} → {self.subject} ({self.assigned_class})"