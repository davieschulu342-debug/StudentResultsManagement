from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import lesson_plan_view

urlpatterns = [
    # ----------------- Home / Index -----------------
    
    path('', views.index, name='index'),


    # ----------------- Admin Authentication -----------------
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('accounts/', include('django.contrib.auth.urls')),

    # ----------------- Teacher Authentication -----------------
    path('teacher-login/', views.teacher_login, name='teacher_login'),
    path('teacher-logout/', views.teacher_logout, name='teacher_logout'),
    path('teacher-register/', views.teacher_register, name='teacher_register'),
    path('generate-lesson-plan/', lesson_plan_view, name='generate_lesson_plan'),
    # ----------------- Dashboard -----------------
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),

    # ----------------- Classes -----------------
    path('classes/create/', views.create_class, name='create_class'),
    path('classes/manage/', views.manage_classes, name='manage_classes'),
    path('classes/edit/<int:class_id>/', views.edit_class, name='edit_class'),
    path('classes/delete/<int:class_id>/', views.delete_class, name='delete_class'),
    path('get_class_details/', views.get_class_details, name='get_class_details'),
    path('download_class_list/<int:class_id>/', views.download_class_list, name='download_class_list'),

    # ----------------- Subjects -----------------
    path('subjects/create/', views.create_subject, name='create_subject'),
    path('subjects/manage/', views.manage_subjects, name='manage_subjects'),  # All subjects
    path('subjects/manage/<int:class_id>/', views.manage_subjects, name='manage_subjects_by_class'),  # By class
    path('subjects/edit/<int:subject_id>/', views.edit_subject, name='edit_subject'),
    path('subjects/delete/<int:subject_id>/', views.delete_subject, name='delete_subject'),

    # ----------------- Subject Combinations -----------------
    path('subject-combinations/add/', views.add_subject_combination, name='add_subject_combination'),
    path('subject-combinations/manage/', views.manage_subject_combination, name='manage_subject_combination'),
    path('subject-combinations/edit/<int:subject_id>/', views.edit_subject_combination, name='edit_subject_combination'),
    path('subject-combinations/delete/<int:subject_id>/', views.delete_subject_combination, name='delete_subject_combination'),

    # ----------------- Students -----------------
    path('students/add/', views.add_student, name='add_student'),
    path('students/manage/', views.manage_students, name='manage_students'),
    path('students/edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('students/delete/<int:student_id>/', views.delete_student, name='delete_student'),

    # ----------------- Notices -----------------
    path('notices/add/', views.add_notice, name='add_notice'),
    path('notices/manage/', views.manage_notice, name='manage_notice'),
    path('notices/edit/<int:notice_id>/', views.edit_notice, name='edit_notice'),
    path('notices/detail/<int:notice_id>/', views.notice_detail, name='notice_detail'),

    # ----------------- Departments -----------------
    path('departments/manage/', views.manage_departments, name='manage_departments'),
    path('departments/add/', views.add_department, name='add_department'),
    path('departments/edit/<int:department_id>/', views.edit_department, name='edit_department'),
    path('departments/delete/<int:department_id>/', views.delete_department, name='delete_department'),

    # ----------------- Teachers -----------------
    path('teachers/add/', views.add_teacher, name='add_teacher'),
    path('teachers/manage/', views.manage_teachers, name='manage_teachers'),
    path('teachers/edit/<int:teacher_id>/', views.edit_teacher, name='edit_teacher'),
    path('teachers/delete/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),

    # ----------------- Results -----------------
    path('results/add/', views.add_result, name='add_result'),
    path(
        'results/enter/<int:class_id>/<int:subject_id>/<str:term>/<int:year>/<str:test_type>/',
        views.enter_marks,
        name='enter_marks'
    ),
    path('results/get-students-subjects/', views.get_students_subjects, name='get_students_subjects'),
    path('results/get-subjects-by-class/', views.get_subjects_by_class, name='get_subjects_by_class'),
    path('results/get-students-by-class/', views.get_students_by_class, name='get_students_by_class'),
    path('results/update/', views.update_results, name='update_results'),  # AJAX
    path('results/get/', views.get_results, name='get_results'),
    path('results/download/', views.download_results_pdf, name='download_results_pdf'),
    path('results/delete/', views.delete_results, name='delete_results'),
    path('results/view/', views.view_results, name='view_results'),
    path('manage_results/', views.manage_results, name='manage_results'),

    # ----------------- Password Reset for Teachers -----------------
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
        auth_views.PasswordResetDoneView.as_view(template_name='teacher/password_reset_done.html'),
        name='teacher_password_reset_done'
    ),
    path(
        'teacher/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(success_url='/teacher/reset/done/', template_name='teacher/password_reset_confirm.html'),
        name='teacher_password_reset_confirm'
    ),
    path(
        'teacher/reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='teacher/password_reset_complete.html'),
        name='teacher_password_reset_complete'
    ),

    # ----------------- Utility / AJAX -----------------
    path('get-class-session/', views.get_class_session, name='get_class_session'),

    # -----------------Downloads ----------------------
    # ----------------- Mark Schedule -----------------
path('class_list_view/', views.class_list_view, name='class_list_view'),
path('marks-schedule/', views.mark_schedule_view, name='mark_schedule'),
path('marks-schedule/download/pdf/', views.download_mark_schedule_pdf, name='download_mark_schedule_pdf'),
path('marks-schedule/download/excel/', views.download_mark_schedule_excel, name='download_mark_schedule_excel'),
path(
    'marks-schedule/download/term/pdf/',
    views.download_term_mark_schedule_pdf,
    name='download_term_mark_schedule_pdf'
),
path('staff/', views.staff_list, name='staff_list'),
path('staff/excel/', views.staff_list_excel, name='staff_list_excel'),
path('staff/pdf/', views.staff_list_pdf, name='staff_list_pdf'),

path('forgot-password/', views.forgot_password, name='forgot_password'),

path('report_form_generator/', views.report_form_generator, name='report_form_generator'),
path('downloads/report-forms/', views.report_form_select_class, name='report_form_select_class'),

 # Messaging
    path('messages/inbox/', views.inbox, name='inbox'),
    path('messages/sent/', views.sent_messages, name='sent_messages'),
    path('messages/send/', views.send_message, name='send_message'),
    path("messages/<int:message_id>/", views.view_message, name="view_message"),
    path('messages/delete/<int:message_id>/', views.delete_message, name='delete_message'),
    path('messages/recipients/', views.message_recipients, name='message_recipients'),
    path('notifications/unread/', views.unread_notifications, name='unread_notifications'),
    path('messages/recent/', views.recent_messages, name='recent_messages'),
    path('messages/read/<int:msg_id>/', views.mark_message_read, name='mark_message_read'),
    path('messages/clear/', views.clear_messages, name='clear_messages'),
    path('messages/<int:message_id>/reply/', views.reply_message, name='reply_message'),

    
    path('notifications_view/', views.notifications_view, name='notifications_view'),
    path('notifications/recent/', views.recent_notifications, name='recent_notifications'),
    path('notifications/mark-read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/clear/', views.clear_notifications, name='clear_notifications'),

    #------------Material download
    path('teacher-material-login/', views.teacher_material_login, name='teacher_material_login'),
    path('downloads/materials/student/login/', views.student_material_login, name='student_material_login'),

    path('downloads/materials/', views.learning_materials, name='learning_materials'),
    path(
        'teacher-materials/',
        views.teacher_materials,
        name='teacher_materials'
    ),

    path(
        'teacher-materials/<str:category>/',
        views.teacher_materials_by_category,
        name='teacher_materials_by_category'
    ),
    
    path(
    'downloads/student/<str:level>/',
    views.student_materials_by_level,
    name='student_materials_by_level'
    ),
    
    path(
    'downloads/student/',
    views.student_materials,
    name='student_materials'
    ),

    path('admin/upload-student-material/', views.upload_student_material, name='upload_student_material'),
    path('admin/upload-teacher-material/', views.upload_teacher_material, name='upload_teacher_material'),
    
    path('upload/materials/', views.upload_materials_dashboard, name='upload_materials_dashboard'),
    path('downloads/materials-selection/', views.materials_selection, name='materials_selection'),

    #ANALYSIS
    path("analysis/junior/", views.junior_analysis_select, name="junior_analysis_select"),
    path(
    "junior-analysis/results/",
    views.junior_analysis_results,
    name="junior_analysis_results"
    ),

    path('analysis/senior/', views.senior_analysis_select, name='senior_analysis_select'),
    path('senior-analysis/results/', views.senior_analysis_results, name='senior_analysis_results'),
    path('junior-analysis/download/', views.download_junior_analysis_excel, name='download_junior_analysis_excel'),
    path('senior-analysis/download/', views.download_senior_analysis_excel, name='download_senior_analysis_excel'),

    path('records-of-work/', views.records_of_work, name='records_of_work'),
    path('schemes-of-work/', views.schemes_of_work_view, name='schemes_of_work'), 

    path('pdf/', views.generate_pdf_zip, name='generate_pdf'),
    path('word/', views.generate_word_zip, name='generate_word'),

    path("student-login/", views.student_login, name="student_login"),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path("results-form/", views.results_form, name="results_form"),
    path('generate-student-report/', views.generate_student_report, name='generate_student_report'),
    path('assign-classes-subjects/', views.assign_classes_subjects, name='assign_classes_subjects'),
    path('delete-assignment/<int:id>/', views.delete_assignment, name='delete_assignment'),
]   

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)