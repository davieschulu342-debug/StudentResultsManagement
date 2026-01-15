from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords 

class Class(models.Model):
    class_name = models.CharField(max_length=100)
    numeric_name = models.IntegerField()
    section = models.CharField(max_length=10)
    creation_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.class_name} {self.numeric_name} {self.section}"
    
class Student(models.Model):
    GENDER_CHOICES = (
        ('Male','Male'),
        ('Female','Female'),
    )
    student_name = models.CharField(max_length=100)
    student_class = models.ForeignKey(Class,on_delete=models.SET_NULL,null=True)
    exam_no = models.CharField(max_length=12, unique=True)
    phone_no = models.EmailField(max_length=100)
    gender = models.CharField(max_length=10,choices=GENDER_CHOICES)
    dob = models.CharField(max_length=20)
    address = models.CharField(max_length=50)
    registration_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)

    def __str__(self):
        return self.student_name
    
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

    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    student_class = models.ForeignKey('Class', on_delete=models.SET_NULL, null=True)
    subject = models.ForeignKey('Subject', on_delete=models.SET_NULL, null=True)

    test_type = models.CharField(max_length=10, choices=TEST_CHOICES)
    term = models.CharField(max_length=10, choices=TERM_CHOICES)
    year = models.IntegerField()

    marks = models.IntegerField()
    posting_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)

    # Simple History
    history = HistoricalRecords(user_model=User)

class Notice(models.Model):
    title = models.CharField(max_length=100)
    details = models.TextField()
    link = models.URLField(max_length=200, blank=True, null=True)  # new field
    posting_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


    def __str__(self):
       return self.title

class TeacherProfile(models.Model):
    GENDER_CHOICES = (('Male','Male'), ('Female','Female'))
    MARITAL_STATUS = (('Single','Single'), ('Married','Married'))

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    teacher_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS)
    emp_no = models.IntegerField()
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    phone_no = models.CharField(max_length=14)
    date_first_app = models.DateField()
    date_current_app = models.DateField()
    date_of_retirement = models.DateField(null=True, blank=True)
    acad_qualif = models.CharField(max_length=50)
    prof_qualif = models.CharField(max_length=100)
    major = models.CharField(max_length=50)
    minor = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.teacher_name} ({self.department})"
   
class Department(models.Model):
    department_name = models.CharField(max_length=100)
    department_code = models.CharField(max_length=10)
    hod = models.CharField(max_length=50)
    no_of_teachers = models.IntegerField(default=0)
    creation_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.department_name
    
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
    dept = instance.department
    if dept:
        dept.no_of_teachers = TeacherProfile.objects.filter(department=dept).count()
        dept.save()


