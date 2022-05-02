from django.contrib import admin

from .models import Application, Company, Resume, Specialty, Vacancy

admin.site.register(Application)
admin.site.register(Company)
admin.site.register(Resume)
admin.site.register(Specialty)
admin.site.register(Vacancy)
