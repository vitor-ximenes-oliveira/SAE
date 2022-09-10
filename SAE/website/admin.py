from django.contrib import admin
from django.db import models
from website.models import Professor,Turmas
from django.contrib.auth.admin import UserAdmin
from django.forms import CheckboxSelectMultiple
from django import forms

class UsuarioAdmin(admin.ModelAdmin):
 pass
admin.site.register(Professor,UsuarioAdmin)
admin.site.register(Turmas,UsuarioAdmin)
