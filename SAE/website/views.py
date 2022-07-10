from datetime import datetime
from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password, check_password
from website.forms import AlunoForm, ProfessorForm
from website.models import Aluno, Professor
from django.contrib import messages
import os
import pythoncom
import win32com.client
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from SAE import settings
from SAE.settings import BASE_DIR, MEDIA_ROOT

def cadastro(request):
    form = AlunoForm(request.POST)
    if request.method == 'POST':
        try: 
            professor = Professor()
            if (professor.esta_ativo == False):
                al_email =  request.POST.get("al_email")
                checar_email = Aluno.objects.get(al_email = al_email)
                if checar_email:
                    messages.info(request, "Já existe um aluno cadastrado com esse e-mail")   
            else:
                al_email =  request.POST.get("al_email")
                checar_email = Professor.objects.get(pf_email = al_email)
                if checar_email:
                    messages.info(request, "Já existe um professor cadastrado com esse e-mail")                 
        except (Aluno.DoesNotExist, Professor.DoesNotExist):
            al_nome = request.POST.get("al_nome")
            al_email = request.POST.get("al_email")
            data = request.POST.get("al_nascimento")
            try:
                al_nascimento = datetime.strptime(data,"%d/%m/%Y")
                al_senha = make_password(request.POST.get("al_senha"))
                professor = Professor()
                if (professor.esta_ativo == False):
                    user = Aluno.objects.create(al_nome=al_nome, al_email=al_email,al_nascimento=al_nascimento,al_senha=al_senha)
                    user.save()    
                else:
                    user = Professor.objects.create(pf_nome=al_nome, pf_email=al_email,pf_nascimento=al_nascimento,pf_senha=al_senha)
                    user.save()
                messages.success(request,"Conta criada com sucesso")           
                return redirect("/login")
            except ValueError:
                messages.info(request, "Formato de data inválida. Insira no seguinte formato: ##/##/####")            
    return render(request, 'cadastro.html', {'form': form})

def login_user(request):        
            if request.method == 'POST':
                try:
                    al_nome = request.POST.get("al_nome")
                    al_senha = request.POST.get("al_senha")
                    user =Aluno.objects.get(al_nome=al_nome)                
                    if user:
                        checar_senha=check_password(al_senha, user.al_senha)
                        if checar_senha:
                            professor = Professor()
                            if (professor.esta_ativo == False):
                                return redirect('/pagina_aluno')
                            else:
                                return redirect('/pagina_professor')                            
                except (Aluno.DoesNotExist, Professor.DoesNotExist):   
                    messages.info(request, "Nome/senha inválido(s)")
            return render(request,"login.html")

def visualizar(request,arquivo):
    extensoes = [".pdf", ".txt", ".png", ".jpg", ".gif", ".bmp",".mp3"]
    if arquivo.endswith(tuple(extensoes)):
        diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)
        arquivo = open(diretorio_arquivo, 'rb') 
        abrir_Arquivo = FileResponse(arquivo)
        return abrir_Arquivo
    elif arquivo.endswith('.xlsx'):
        diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)
        excel = win32com.client.Dispatch('Excel.Application',pythoncom.CoInitialize())
        excel.Visible = True
        abrir_excel = excel.Workbooks.Open(diretorio_arquivo, None,True)
        return HttpResponseRedirect("/atividades") 
    elif arquivo.endswith('.docx'): 
        diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)
        word=win32com.client.Dispatch("Word.Application",pythoncom.CoInitialize())
        word.Visible = True
        abrir_excel = word.Documents.Open(diretorio_arquivo, None,True)
        return HttpResponseRedirect("/atividades") 
    elif arquivo.endswith('.pptx'):
        diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)
        PowerPoint = win32com.client.Dispatch("Powerpoint.Application",pythoncom.CoInitialize())
        PowerPoint.Visible = True
        Abrir_PowerPoint = PowerPoint.Presentations.Open(diretorio_arquivo, None,True)
        return HttpResponseRedirect("/atividades") 
    else:
        diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)
        os.system(diretorio_arquivo)    
        return HttpResponseRedirect("/atividades") 
    
def baixar(request, arquivo):
    if arquivo != '':
        diretorio_arquivo = (os.path.join(settings.MEDIA_ROOT, arquivo))
        diretorio = open(diretorio_arquivo,'rb')
        download_arquivo = HttpResponse(diretorio ,content_type="aplicacao/arquivo")
        download_arquivo ['Content-Disposition'] = "attachment; nome_arquivo=" + arquivo
        return download_arquivo
    else:
        return render(request ,'atividades.html')    

def pagina_aluno(request):
    form = AlunoForm(request.POST)
    return render(request,"pagina_aluno.html")

def pagina_professor(request):
    form = ProfessorForm(request.POST)
    return render(request,"pagina_professor.html")
