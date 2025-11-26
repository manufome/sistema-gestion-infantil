from django.contrib import admin
from .models import Student, Attendance, AcademicProgress

admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(AcademicProgress)
