from django.contrib import admin
from website.models import Professor,Turmas

class UsuarioAdmin(admin.ModelAdmin):
    exclude = ('pf_nome',)
admin.site.register(Professor,UsuarioAdmin)
