from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, University, Program, Requirement, Application, Document

# تسجيل جدول المستخدمين المخصص
admin.site.register(User, UserAdmin)

# تسجيل باقي الجداول الأساسية
admin.site.register(University)
admin.site.register(Program)
admin.site.register(Requirement)
admin.site.register(Application)
admin.site.register(Document)