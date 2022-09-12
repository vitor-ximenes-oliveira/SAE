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
    path('',views.login_user,name='login'),
    path('admin/', admin.site.urls),
    path('Teladecadastroaluno', views.cadastro,name='Teladecadastroaluno'),
    path('CadastroProfessor',views.cadastro,name='CadastroProfessor'),
    path('login',views.login_user,name='login'),
    path('telaProfessor/<int:idProfessor>',views.pagina_professor,name='telaProfessor'),
    path('baixar_arquivo/<str:arquivo>',views.baixar_arquivo, name='baixar_arquivo'),
    path('visualizar_arquivo/<str:arquivo>',views.visualizar_arquivo, name='visualizar_arquivo'),
    path('feedback/<int:ra>',views.feedback, name="feedback"),
    path('sair',views.sair),
    path('turmas/<int:idProfessor>',views.turmas),
    path('enviar_arquivo/<int:idProfessor>',views.enviar_arquivo,name='enviar_arquivo'),
    path('atividades/<int:ra>',views.atividades,name='atividades'),
    path('inserir_classe',views.inserir_classe,name='inserir_classe'),
    path('graficosFeedback', views.graficosFeedback, name="graficosFeedback"),
    path('criarFormulario', views.criarFormulario, name='criarFormulario'),
    path('gabaritoFormulario', views.gabaritoFormulario),
    path('telaAluno/<int:ra>', views.telaAluno, name='telaAluno'),
    path('preencherGabarito/<int:idProfessor', views.preencherGabarito),
    path('telaAluno', views.telaAluno, name="telaAluno"),
    url(r'^editar_classe/(?P<idProfessor>[0-9]*)',views.editar_classe,name="editar_classe"),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
