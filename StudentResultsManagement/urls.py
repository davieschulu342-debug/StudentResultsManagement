"""
URL configuration for StudentResultsManagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from ResultsApp.views import (
    index, admin_login, admin_dashboard, create_class, admin_logout, manage_classes, 
    delete_class, edit_class, create_subject, manage_subjects, edit_subject, delete_subject, 
    add_subject_combination, manage_subject_combination, edit_subject_combination, delete_subject_combination, 
    add_student, edit_student, manage_students, delete_student, add_notice, manage_notice, edit_notice, 
    add_result, get_students_subjects, get_subjects_by_class, get_students_by_class, update_results, 
    get_results, download_results_pdf, delete_results, view_results, 
    teacher_register, teacher_login, teacher_dashboard, manage_results, manage_departments, add_department, edit_department, delete_department, notice_detail, teacher_logout, add_teacher, manage_teachers,edit_teacher, delete_teacher, forgot_password, reset_password 
)
from django.urls import path, include
from django.http import JsonResponse



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ResultsApp.urls')),
    path('', index, name='index'),
    path('admin-login/', admin_login, name='admin_login'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('create-class/', create_class, name='create_class'),
    path('admin_logout/', admin_logout, name='admin_logout'),
    path('manage_classes/', manage_classes, name='manage_classes'),
    path('edit-class/<int:class_id>/', edit_class, name='edit_class'),
    path('delete-class/<int:class_id>/', delete_class, name='delete_class'),
    path('create_subject/', create_subject, name='create_subject'),
    path('manage_subjects/', manage_subjects, name='manage_subjects'),
    path('edit-subject/<int:subject_id>/', edit_subject, name='edit_subject'),
    path('delete-subject/<int:subject_id>/', delete_subject, name='delete_subject'),
    path('add_subject_combination/', add_subject_combination, name='add_subject_combination'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('manage_subject_combination/', manage_subject_combination, name='manage_subject_combination'),
    path('edit-subject-combination/<int:subject_id>/', edit_subject_combination, name='edit_subject_combination'),
    path('delete-subject-combination/<int:subject_id>/', delete_subject_combination, name='delete_subject_combination'),
    path('add_student/', add_student, name='add_student'),
    path('edit-student/<int:student_id>/', edit_student, name='edit_student'),
    path('manage-students/', manage_students, name= 'manage_students'),
    path('delete-student/<int:student_id>/', delete_student, name='delete_student'),
    path('add-notice/', add_notice, name='add_notice'),
    path('edit-notice/<int:notice_id>/', edit_notice, name='edit_notice'),
    path('manage_notice/', manage_notice, name='manage_notice'),
    path('add_result/', add_result, name='add_result'),
    path('get-students-subjects/', get_students_subjects, name='get_students_subjects'),
    path('manage_results/<int:class_id>/', manage_results, name='manage_results'),
    path('get-subjects-by-class/', get_subjects_by_class, name='get_subjects_by_class'),
    path('get_results/', get_results, name='get_results'),
    path('update_results/', update_results, name='update_results'), # AJAX endpoint
    path('download-results/', download_results_pdf, name="download_results_pdf"),
    path('delete_results/', delete_results, name='delete_results'),
    path('view_results/', view_results, name="view_results"),
     path('teacher_register/', teacher_register, name='teacher_register'),
    path('teacher_login/', teacher_login, name='teacher_login'),
    path('teacher_dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('manage-departments/', manage_departments, name='manage_departments'),
    path('add-department/', add_department, name='add_department'),
    path('edit-department/<int:department_id>/', edit_department, name='edit_department'),
    path('delete-department/<int:department_id>/', delete_department, name='delete_department'),
    path('notice_detail/<int:notice_id>/', notice_detail, name='notice_detail'),
    path('teacher_logout/', teacher_logout, name='teacher_logout'),
    path('teacher_dashboard/',teacher_dashboard, name='teacher_dashboard'),
    path('add-teacher/', add_teacher, name='add_teacher'),
    path('manage-teachers/', manage_teachers, name='manage_teachers'),
    path('edit_teacher/<int:teacher_id>/', edit_teacher, name='edit_teacher'),
    path('delete_teacher/<int:teacher_id>/', delete_teacher, name='delete_teacher'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/', reset_password, name='reset_password'),
    path('teacher_logout/', teacher_logout, name='teacher_logout'),
     path(
        'teacher/password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='teacher/password_reset.html',
            email_template_name='teacher/password_reset_email.html',
            success_url='/teacher/password-reset/done/'
        ),
        name='teacher_password_reset'
    ),
    path(
        'teacher/password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='teacher/password_reset_done.html'
        ),
        name='teacher_password_reset_done'
    ),
    path(
        'teacher/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='teacher/password_reset_confirm.html',
            success_url='/teacher/reset/done/'
        ),
        name='teacher_password_reset_confirm'
    ),
    path(
        'teacher/reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='teacher/password_reset_complete.html'
        ),
        name='teacher_password_reset_complete'
    ),


]
