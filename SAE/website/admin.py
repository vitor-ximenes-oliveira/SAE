from django.contrib import admin
from website.models import Professor
from django.contrib.auth.admin import UserAdmin

class UsuarioAdmin(admin.ModelAdmin):
 pass
admin.site.register(Professor,UsuarioAdmin)
