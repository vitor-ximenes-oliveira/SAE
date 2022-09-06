from datetime import datetime
from urllib.request import Request
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password, check_password
#from urllib3 import HTTPResponse
from website.forms import AlunoForm, FeedBackForm, ProfessorForm
from website.models import Aluno, Feedback, Professor, Turmas
from django.contrib import messages
import os
#import pythoncom
#import win32com.client
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from SAE import settings
from SAE.settings import BASE_DIR, MEDIA_ROOT
from django.contrib.auth import login,authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import matplotlib as plt

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
            al_nascimento = request.POST.get("al_nascimento")
            try:
                al_senha = make_password(request.POST.get("al_senha"))
                professor = Professor()
                if (professor.esta_ativo == False):
                    al_nome = request.POST.get("al_nome")
                    al_senha = make_password(request.POST.get("al_senha"))
                    autenticar_usuario = User(username=al_nome, password=al_senha)
                    autenticar_usuario.save()       
                    user = Aluno.objects.create(al_nome=al_nome, al_email=al_email,al_nascimento=al_nascimento,al_senha=al_senha)
                    user.save()    
                else:
                    al_nome = request.POST.get("al_nome")
                    al_senha = make_password(request.POST.get("al_senha"))
                    autenticar_usuario = User(username=al_nome, password=al_senha)
                    autenticar_usuario.save()       
                    user = Professor.objects.create(pf_nome=al_nome, pf_email=al_email,pf_nascimento=al_nascimento,pf_senha=al_senha)
                    user.save()
                messages.success(request,"Conta criada com sucesso")           
                return redirect("/login")
            except ValueError:
                messages.info(request, "Formato de data inválida. Insira no seguinte formato: ##/##/####")            
    return render(request, 'CadastroProfessor.html', {'form': form})

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
                                autenticar_usuario = authenticate(username=al_nome, password=al_senha, backend= 'django.contrib.auth.backends.AllowAllUsersModelBackend')                    
                                login(request, autenticar_usuario)
                                return redirect('/pagina_aluno')
                            else:                
                                autenticar_usuario = authenticate(username=al_nome, password=al_senha, backend= 'django.contrib.auth.backends.AllowAllUsersModelBackend')            
                                login(request, autenticar_usuario)
                                return redirect('/pagina_professor')                            
                except (Aluno.DoesNotExist, Professor.DoesNotExist):   
                    messages.info(request, "Nome/senha inválido(s)")
                except (Aluno.MultipleObjectsReturned,Professor.DoesNotExist):
                    autenticar_usuario = User.objects.filter(username=al_nome).first()
                    if autenticar_usuario:
                        login(request, autenticar_usuario)
                        if (professor.esta_ativo == False):
                            return redirect('/pagina_aluno')
                        else:
                            login(request, autenticar_usuario)
                            return redirect('/pagina_professor')  
            return render(request,"login.html")

@login_required(login_url='/login')
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

@login_required(login_url='/login')
def baixar(request, arquivo):
    if arquivo != '':
        diretorio_arquivo = (os.path.join(settings.MEDIA_ROOT, arquivo))
        diretorio = open(diretorio_arquivo,'rb')
        download_arquivo = HttpResponse(diretorio ,content_type="aplicacao/arquivo")
        download_arquivo ['Content-Disposition'] = "attachment; nome_arquivo=" + arquivo
        return download_arquivo
    else:
        return render(request ,'atividades.html')

#@login_required(login_url='/login')
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
    return render(request, 'feedback.html',  {'form': form})

@login_required(login_url='/login')
def sair(request):
    logout(request)
    messages.success(request,"Você saiu do seu perfil")
    return HttpResponseRedirect('/login')

def turmas(request,idProfessor):
        if request.method == 'POST':
            classe = request.POST.get('classe')
            alunos = Turmas.objects.raw("select idTurma, a.al_nome from turmas t join aluno a on t.alu_id = a.ra join Professor p on t.prof_id = idProfessor where t.classe =%s and t.prof_id = %s group by a.al_nome",(str(classe),str(idProfessor)))
            turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe",str(idProfessor))
        else:
            alunos = ""
            turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe",str(idProfessor))         
        return render(request, 'turmas.html', {'turmas': turmas,'alunos':alunos})

@login_required(login_url='/login')
def pagina_aluno(request):
    form = AlunoForm(request.POST)
    return render(request,"pagina_aluno.html")

#@login_required(login_url='/login')
def pagina_professor(request):
    form = ProfessorForm(request.POST)
    return render(request,"telaProfessor.html")


def teste(request):

    ruim = 0
    bom = 0
    medio = 0
    excelente = 0

    ruim2 = 0
    bom2 = 0
    medio2 = 0
    excelente2 = 0

    ruim3 = 0
    bom3 = 0
    medio3 = 0
    excelente3 = 0

    ruim4 = 0
    bom4 = 0
    medio4 = 0
    excelente4 = 0

    ruim5 = 0
    bom5 = 0
    medio5 = 0
    excelente5 = 0

    ruim6 = 0
    bom6 = 0
    medio6 = 0
    excelente6 = 0

    ruim7 = 0
    bom7 = 0
    medio7 = 0
    excelente7 = 0

    ruim8 = 0
    bom8 = 0
    medio8 = 0
    excelente8 = 0

    ruim9 = 0
    bom9 = 0
    medio9 = 0
    excelente9 = 0

    pergunta1 = Feedback.objects.values_list("pergunta1", flat=True)

    for x in pergunta1:
        if(x == 'Ruim'):
            ruim+=1
        elif(x == 'Bom'):
            bom+=1
        elif(x == 'Ótimo'):
            medio+=1
        else:
            excelente+=1


    pergunta2 = Feedback.objects.values_list("pergunta2", flat=True)

    for x in pergunta2:
        if(x == 'Ruim'):
            ruim2+=1
        elif(x == 'Bom'):
            bom2+=1
        elif(x == 'Ótimo'):
            medio2+=1
        else:
            excelente2+=1

    pergunta3 = Feedback.objects.values_list("pergunta3", flat=True)

    for x in pergunta3:
        if(x == 'Ruim'):
            ruim3+=1
        elif(x == 'Bom'):
            bom3+=1
        elif(x == 'Ótimo'):
            medio3+=1
        else:
            excelente3+=1

    pergunta4 = Feedback.objects.values_list("pergunta4", flat=True)

    for x in pergunta4:
        if(x == 'Ruim'):
            ruim4+=1
        elif(x == 'Bom'):
            bom4+=1
        elif(x == 'Ótimo'):
            medio4+=1
        else:
            excelente4+=1

    pergunta5 = Feedback.objects.values_list("pergunta5", flat=True)

    for x in pergunta5:
        if(x == 'Ruim'):
            ruim5+=1
        elif(x == 'Bom'):
            bom5+=1
        elif(x == 'Ótimo'):
            medio5+=1
        else:
            excelente5+=1

    pergunta6 = Feedback.objects.values_list("pergunta6", flat=True)

    for x in pergunta6:
        if(x == 'Ruim'):
            ruim6+=1
        elif(x == 'Bom'):
            bom6+=1
        elif(x == 'Ótimo'):
            medio6+=1
        else:
            excelente6+=1

    pergunta7 = Feedback.objects.values_list("pergunta7", flat=True)

    for x in pergunta7:
        if(x == 'Ruim'):
            ruim7+=1
        elif(x == 'Bom'):
            bom7+=1
        elif(x == 'Ótimo'):
            medio7+=1
        else:
            excelente7+=1

    pergunta8 = Feedback.objects.values_list("pergunta8", flat=True)

    for x in pergunta8:
        if(x == 'Ruim'):
            ruim8+=1
        elif(x == 'Bom'):
            bom8+=1
        elif(x == 'Ótimo'):
            medio8+=1
        else:
            excelente8+=1

    pergunta9 = Feedback.objects.values_list("pergunta9", flat=True)

    for x in pergunta9:
        if(x == 'Ruim'):
            ruim9+=1
        elif(x == 'Bom'):
            bom9+=1
        elif(x == 'Ótimo'):
            medio9+=1
        else:
            excelente9+=1        
    return render(request, "graficosFeedback.html" , {"ruim" : ruim, "bom" : bom, "medio" : medio , "excelente": excelente, "ruim2" : ruim2, "bom2" : bom2, "medio2" : medio2 , "excelente2": excelente2, "ruim3" : ruim3, "bom3" : bom3, "medio3" : medio3 , "excelente3": excelente3, "ruim4" : ruim4, "bom4" : bom4, "medio4" : medio4 , "excelente4": excelente4, "ruim5" : ruim5, "bom5" : bom5, "medio5" : medio5 , "excelente5": excelente5, "ruim6" : ruim6, "bom6" : bom6, "medio6" : medio6 , "excelente6": excelente6, "ruim7" : ruim7, "bom7" : bom7, "medio7" : medio7 , "excelente7": excelente7, "ruim8" : ruim8, "bom8" : bom8, "medio8" : medio8 , "excelente8": excelente8, "ruim9" : ruim9, "bom9" : bom9, "medio9" : medio9 , "excelente9": excelente9})
                
           
