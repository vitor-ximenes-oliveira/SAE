"""SAE URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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

from django import views
from django.contrib import admin
from django.urls import path
from website import views
from django.conf.urls import url
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cadastro', views.cadastro),
    path('login',views.login_user),
    path('pagina_aluno',views.pagina_aluno),
    path('telaProfessor/<int:idProfessor>',views.pagina_professor,name='telaProfessor'),
    path('baixar/<str:arquivo>',views.baixar, name='baixar'),
    path('visualizar/<str:arquivo>',views.visualizar, name='visualizar'),
    path('feedback',views.feedback),
    path('sair',views.sair),
    path('turmas/<int:idProfessor>',views.turmas),
    path('enviar_arquivo/<int:idProfessor>',views.enviar_arquivo,name='enviar_arquivo'),
    path('telaProfessor/<int:idProfessor>',views.pagina_professor),
    path('atividades/<int:ra>',views.atividades,name='atividades'),
    path('inserir_classe',views.inserir_classe,name='inserir_classe'),
    url(r'^editar_classe/(?P<idProfessor>[0-9]*)',views.editar_classe,name="editar_classe"),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
