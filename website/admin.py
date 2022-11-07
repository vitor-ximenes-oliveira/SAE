from xml.etree.ElementInclude import include
from django.contrib import admin
from website import models
from website.models import Professor
from django.conf import settings

class UsuarioAdmin(admin.ModelAdmin):
    exclude = ('Nome','isProf')
    include = ('Materia', 'Nascimento')
admin.site.register(Professor,UsuarioAdmin)


   

