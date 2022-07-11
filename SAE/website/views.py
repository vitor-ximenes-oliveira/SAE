from datetime import datetime
from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password, check_password
from website.forms import AlunoForm, ProfessorForm, FeedBackForm
from website.models import Aluno, Professor, Feedback
from django.contrib import messages
import os
import pythoncom
import win32com.client
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from SAE import settings
from SAE.settings import BASE_DIR, MEDIA_ROOT
from django.db import DataError, IntegrityError

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

def feedback(request):
    form = FeedBackForm(request.POST)
    if request.method == 'POST':
        try:
            justificativa1 = request.POST.get("Justificativa1")
            justificativa2 = request.POST.get("Justificativa2")
            justificativa3 = request.POST.get("Justificativa3")             
            justificativa4 = request.POST.get("Justificativa4")             
            justificativa5 = request.POST.get("Justificativa5")             
            justificativa6 = request.POST.get("Justificativa6")             
            justificativa7 = request.POST.get("Justificativa7")             
            justificativa8 = request.POST.get("Justificativa8")             
            justificativa9 = request.POST.get("Justificativa9")
            pergunta1 = request.POST.get("btn-radio")
            pergunta2 = request.POST.get("btn-radio2")
            pergunta3 = request.POST.get("btn-radio3")
            pergunta4 = request.POST.get("btn-radio4")
            pergunta5 = request.POST.get("btn-radio5")
            pergunta6 = request.POST.get("btn-radio6")
            pergunta7 = request.POST.get("btn-radio7")
            pergunta8 = request.POST.get("btn-radio8")
            pergunta9 = request.POST.get("btn-radio9")
            feedback = Feedback.objects.create(pergunta1=pergunta1,justificativa1=justificativa1,pergunta2=pergunta2,justificativa2=justificativa2,pergunta3=pergunta3,justificativa3=justificativa3,pergunta4=pergunta4,justificativa4=justificativa4,pergunta5=pergunta5,justificativa5=justificativa5,pergunta6=pergunta6,justificativa6=justificativa6,pergunta7=pergunta7,justificativa7=justificativa7,pergunta8=pergunta8,justificativa8=justificativa8,pergunta9=pergunta9,justificativa9=justificativa9)
            feedback.save() 
            messages.success(request,"Feedback enviado com sucesso")           
            return redirect("/feedback")
        except IntegrityError:
            messages.error(request, "Preencha todos os campos")
    return render(request, 'feedback.html', {'form': form})
    
def pagina_aluno(request):
    form = AlunoForm(request.POST)
    return render(request,"pagina_aluno.html")

def pagina_professor(request):
    form = ProfessorForm(request.POST)
    return render(request,"pagina_professor.html")
