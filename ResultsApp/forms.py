from django import forms
from django.contrib.auth.models import User
from .models import TeacherProfile, Department   # ✅ IMPORT ADDED
from .models import Notice, Student, Subject
from .models import TeacherProfile, GENDER_CHOICES, NATIONALITY_CHOICES, NEXT_OF_KIN_RELATIONSHIP_CHOICES, MARITAL_STATUS_CHOICES, DISABILITY_CHOICES
from django.forms import ClearableFileInput
from .models import Class, Result
from .models import Message
from .models import RecordOfWork

# Choice constants
GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
)

MARITAL_STATUS_CHOICES = (
    ('Single', 'Single'),
    ('Married', 'Married'),
    ('Divorced', 'Divorced'),
    ('Widowed', 'Widowed'),
)

DISABILITY_CHOICES = (
    ('none', 'None'),
    ('physical', 'Physical'),
    ('visual', 'Visual'),
    ('hearing', 'Hearing'),
    ('other', 'Other'),
)

NATIONALITY_CHOICES = (
    ('ZAMBIAN', 'Zambian'),
    ('FOREIGN', 'Foreign'),
)

NEXT_OF_KIN_RELATIONSHIP_CHOICES = (
    ('PARENT', 'Parent'),
    ('SPOUSE', 'Spouse'),
    ('SIBLING', 'Sibling'),
    ('CHILD', 'Child'),
    ('GUARDIAN', 'Guardian'),
    ('OTHER', 'Other'),
)


class TeacherRegistrationForm(forms.ModelForm):
    # User-related fields
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'})
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'})
    )
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'})
    )

    # Choice fields
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    nationality = forms.ChoiceField(
        choices=NATIONALITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    next_of_kin_relationship = forms.ChoiceField(
        choices=NEXT_OF_KIN_RELATIONSHIP_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    marital_status = forms.ChoiceField(
        choices=MARITAL_STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    disability = forms.ChoiceField(
        choices=DISABILITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Optional secondary department
    department2 = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Select secondary department (optional)"
    )

    # Many-to-many: classes & subjects
    classes = forms.ModelMultipleChoiceField(
        queryset=Class.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = TeacherProfile
        fields = [
            'surname',
            'first_name',
            'other_names',
            'gender',
            'nationality',
            'marital_status',
            'date_of_birth',
            'phone_no',
            'department1',
            'department2',
            'academic_qualification',
            'professional_qualification',
            'minor',
            'major',
            'college_university',
            'year_of_graduation',
            'position_first_app',
            'substantive_position',
            'current_position',
            'confirmed',
            'date_first_app',
            'date_current_app',
            'date_of_retirement',
            'pay_point',
            'district_of_pay_point',
            'salary_scale',
            'next_of_kin_name',
            'next_of_kin_phone',
            'next_of_kin_relationship',
            'next_of_kin_district',
            'bank_name',
            'account_number',
            'branch_name',
            'current_station',
            'district',
            'distance_from_DEBs',
            'NRC_No',
            'TCZ_No',
            'TS_No',
            'Employ_No',
            'disability',
            'photo',
            'classes',
            'subjects',
        ]
        widgets = {
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'other_names': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_no': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'department1': forms.Select(attrs={'class': 'form-select'}),
            'academic_qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'professional_qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'minor': forms.TextInput(attrs={'class': 'form-control'}),
            'major': forms.TextInput(attrs={'class': 'form-control'}),
            'college_university': forms.TextInput(attrs={'class': 'form-control'}),
            'year_of_graduation': forms.NumberInput(attrs={'class': 'form-control'}),
            'position_first_app': forms.TextInput(attrs={'class': 'form-control'}),
            'substantive_position': forms.TextInput(attrs={'class': 'form-control'}),
            'current_position': forms.TextInput(attrs={'class': 'form-control'}),
            'date_first_app': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_current_app': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_of_retirement': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'pay_point': forms.TextInput(attrs={'class': 'form-control'}),
            'district_of_pay_point': forms.TextInput(attrs={'class': 'form-control'}),
            'salary_scale': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_name': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_district': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'branch_name': forms.TextInput(attrs={'class': 'form-control'}),
            'current_station': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'distance_from_DEBs': forms.NumberInput(attrs={'class': 'form-control'}),
            'NRC_No': forms.TextInput(attrs={'class': 'form-control'}),
            'TCZ_No': forms.TextInput(attrs={'class': 'form-control'}),
            'TS_No': forms.TextInput(attrs={'class': 'form-control'}),
            'Employ_No': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': ClearableFileInput(attrs={'class': 'form-control'}),
        }

    # Custom validation
    def clean(self):
        cleaned = super().clean()

        # Password match
        if cleaned.get('password') or cleaned.get('confirm_password'):
            if cleaned.get('password') != cleaned.get('confirm_password'):
                raise forms.ValidationError("Passwords do not match.")

        # Primary & secondary department check
        if cleaned.get('department1') and cleaned.get('department1') == cleaned.get('department2'):
            raise forms.ValidationError("Primary and Secondary departments cannot be the same.")

        # Email uniqueness on creation
        if not self.instance.pk and User.objects.filter(username=cleaned.get('email')).exists():
            raise forms.ValidationError("User with this email already exists.")

        return cleaned

    # Save method: creates/updates User + TeacherProfile
    def save(self, commit=True):
        teacher_profile = super().save(commit=False)

        # Handle User object
        if self.cleaned_data.get('email'):
            if self.instance.pk:
                # Update existing user
                teacher_profile.user.email = self.cleaned_data['email']
                teacher_profile.user.username = self.cleaned_data['email']
            else:
                # Create new user
                user = User.objects.create_user(
                    username=self.cleaned_data['email'],
                    email=self.cleaned_data['email'],
                    password=self.cleaned_data.get('password') or User.objects.make_random_password()
                )
                teacher_profile.user = user

        # Update password if provided
        if self.cleaned_data.get('password'):
            teacher_profile.user.set_password(self.cleaned_data['password'])
            teacher_profile.user.save()

        if commit:
            teacher_profile.save()
            self.save_m2m()

        return teacher_profile
        
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = [
            'department_name',
            'department_code',
            'hod',
        ]

        widgets = {
            'department_name': forms.TextInput(attrs={'class': 'form-control'}),
            'department_code': forms.TextInput(attrs={'class': 'form-control'}),
            'hod': forms.TextInput(attrs={'class': 'form-control'}),
        }

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'details', 'link', 'image', 'attachment']
        widgets = {
            'details': forms.Textarea(attrs={'rows': 5}),
        }


from django.core.exceptions import ValidationError
class StudentForm(forms.ModelForm):

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')

        if photo:
            if photo.size > 2 * 1024 * 1024:  # 2MB
                raise ValidationError("Photo size must not exceed 2MB")

        return photo

    class Meta:
        model = Student
        fields = [
            'first_name',
            'last_name',
            'student_class',
            'gender',
            'exam_no',
            'phone_no',
            'dob',
            'address',
            'parent_name',
            'disability',
            'photo',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'student_class': forms.Select(attrs={'class': 'form-select'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'exam_no': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_no': forms.TextInput(attrs={'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'parent_name': forms.TextInput(attrs={'class': 'form-control'}),
            'disability': forms.Select(attrs={'class': 'form-select'}),

            # 👇 optional enhancement added below
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔹 Hide ALL years from the dropdown label
        self.fields['student_class'].label_from_instance = (
            lambda obj: f"{obj.class_name} {obj.numeric_name}{obj.section}"
        )

class ResultsAnalysisForm(forms.Form):
    student_class = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        label="Class"
    )
    term = forms.ChoiceField(
        choices=Result.TERM_CHOICES
    )
    test_type = forms.ChoiceField(
        choices=Result.TEST_CHOICES
    )
    year = forms.IntegerField(required=False)


from django.contrib.auth import get_user_model

User = get_user_model()

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body']
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your message...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional: only staff users can be recipients
        self.fields['recipient'].queryset = User.objects.filter(is_staff=True)

#MATERIAL FORMS
from django import forms
from .models import TeacherMaterial, StudentMaterial

# ---------------- Teacher Material Form ----------------
class TeacherMaterialForm(forms.ModelForm):
    class Meta:
        model = TeacherMaterial
        fields = ['title', 'description', 'category', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.ppt,.pptx'}),
        }


# ---------------- Student Material Form ----------------
class StudentMaterialForm(forms.ModelForm):
    class Meta:
        model = StudentMaterial
        fields = ['title', 'description', 'level', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.ppt,.pptx'}),
        }


class RecordOfWorkForm(forms.ModelForm):
    class Meta:
        model = RecordOfWork
        fields = [
            'subject', 'year', 'term', 'grade',
            'week', 'work_done', 'work_not_done',
            'teacher_comments', 'hod_remarks'
        ]
        widgets = {
            'work_done': forms.Textarea(attrs={'rows': 3}),
            'work_not_done': forms.Textarea(attrs={'rows': 3}),
            'teacher_comments': forms.Textarea(attrs={'rows': 3}),
            'hod_remarks': forms.Textarea(attrs={'rows': 3}),
        }