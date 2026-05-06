from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Avg
from collections import defaultdict
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    Class, Student, Subject, Notice, SubjectCombination, Department, 
    TeacherProfile, GradingSystem, Grade, Result
)

# ======= Grading System Admin =======
class GradeInline(admin.TabularInline):
    model = Grade
    extra = 1

@admin.register(GradingSystem)
class GradingSystemAdmin(admin.ModelAdmin):
    inlines = [GradeInline]
    list_display = ['class_level']

from django.contrib import admin
from .models import TeacherMaterial, StudentMaterial

@admin.register(TeacherMaterial)
class TeacherMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_by', 'uploaded_at')
    list_filter = ('category',)

@admin.register(StudentMaterial)
class StudentMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'uploaded_by', 'uploaded_at')
    list_filter = ('level',)

# ======= Other models =======
admin.site.register(Class)
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(Result)
admin.site.register(Notice)
admin.site.register(SubjectCombination)
admin.site.register(Department)
admin.site.register(TeacherProfile)
