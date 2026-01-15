from django.contrib import admin
from .models import *
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Result

class ResultAdmin(SimpleHistoryAdmin):
    class ResultAdmin(SimpleHistoryAdmin):
     list_display = ("student", "marks", "test_type", "term", "year", "posting_date", "updation_date")
     list_filter = ("student_class", "subject", "test_type", "term", "year")
     search_fields = ("student__name", "subject__name")

admin.site.register(Class)
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(Result)
admin.site.register(Notice)
admin.site.register(SubjectCombination)
admin.site.register(Department)

