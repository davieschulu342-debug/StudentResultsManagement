from django import forms
from django.contrib.auth.models import User
from .models import TeacherProfile, Department   # ✅ IMPORT ADDED
from .models import Notice


class TeacherRegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    
    date_first_app = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-lg'})
    )
    date_current_app = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-lg'})
    )
    date_of_retirement = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-lg'})
    )

    class Meta:
        model = TeacherProfile
        fields = [
            'teacher_name',
            'gender',
            'marital_status',
            'emp_no',
            'department',
            'phone_no',
            'date_first_app',
            'date_current_app',
            'date_of_retirement',
            'acad_qualif',
            'prof_qualif',
            'major',
            'minor'
        ]

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("A teacher with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )

        teacher_profile = super().save(commit=False)
        teacher_profile.user = user

        if commit:
            teacher_profile.save()
        
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
        fields = ['title', 'details', 'link'] 


