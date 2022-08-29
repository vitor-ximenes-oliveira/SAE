import stat
from django.db.models.functions import Concat
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password, check_password
from website.models import Aluno, EnviarArquivo, Feedback, Professor, Turmas
from django.contrib import messages
import os
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from SAE import settings
from SAE.settings import BASE_DIR, MEDIA_ROOT
from django.contrib.auth import login,authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User  
from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from djangoconvertvdoctopdf.convertor import StreamingConvertedPdf
from pptx import Presentation
import pandas as pd
import os
import subprocess as sp
import pandas as pd

def cadastro(request):
    if request.method == 'POST':
        try: 
            professor = Professor()
            if (professor.esta_ativo == False):
                al_email = request.POST.get("al_email")
                checar_email = Aluno.objects.get(al_email = al_email)
                if checar_email:
                    messages.error(request, "Já existe um aluno cadastrado com esse e-mail")   
            else:
                al_email =  request.POST.get("al_email")
                checar_email = Professor.objects.get(pf_email = al_email)
                if checar_email:
                    messages.error(request, "Já existe um professor cadastrado com esse e-mail")                 
        except (Aluno.DoesNotExist, Professor.DoesNotExist):
            al_nome = request.POST.get("al_nome")
            al_email = request.POST.get("al_email")
            al_nascimento = request.POST.get("al_nascimento")
            try:
                validate_email(al_email)
            except ValidationError:
                messages.error(request,"Insira um endereço de email válido")
                return redirect('/cadastro')
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
            except (ValueError,ValidationError):
                messages.info(request, "Data de nascimento inválida")  
            except (Aluno.MultipleObjectsReturned,Professor.MultipleObjectsReturned,IntegrityError):  
                messages.error(request,"Preencha todos os campos")
             
    return render(request, 'cadastro.html')

def login_user(request):        
            if 'login' in request.POST:
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
                except (Aluno.MultipleObjectsReturned,Professor.DoesNotExist,User.MultipleObjectsReturned):
                    autenticar_usuario = User.objects.filter(username=al_nome).first()
                    if autenticar_usuario:
                        login(request, autenticar_usuario)
                        professor = Professor()
                        if (professor.esta_ativo == False):
                            return redirect('/pagina_aluno')
                        else:
                            login(request, autenticar_usuario)
                            return redirect('/pagina_professor')
            elif 'cadastro' in request.POST:
                return redirect('/cadastro')  
            return render(request,"login.html")

def atividades(request, ra):
    material_aluno = EnviarArquivo.objects.filter(alu=ra)
    return render(request,'atividades.html',{'material_aluno':material_aluno})

def visualizar(request,arquivo):
    extensoes = [".pdf", ".txt", ".png", ".jpg", ".gif", ".bmp",".mp3",".mp4"]
    if arquivo.endswith(tuple(extensoes)):
        diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)
        arquivo = open(diretorio_arquivo, 'rb') 
        abrir_Arquivo = FileResponse(arquivo)
        return abrir_Arquivo
    elif arquivo.endswith('.xlsx'):
        diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)
        os.system(diretorio_arquivo)    
        os.chmod(diretorio_arquivo,stat.S_IRWXO)                   
        alu = request.GET.get("alu",'')      
        return redirect('../atividades/'+str(alu))
    elif arquivo.endswith('.docx'): 
        diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)
        sp.Popen(["C:\Program Files\Windows NT\Accessories\WordPad.exe", diretorio_arquivo])
        os.chmod(diretorio_arquivo,stat.S_IWUSR and stat.S_IRUSR and stat.S_IRUSR)  

        alu = request.GET.get("alu",'')      
        return redirect('../atividades/'+str(alu))
    elif arquivo.endswith('.pptx'):
        diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)
        os.system(diretorio_arquivo)    
        os.chmod(diretorio_arquivo,stat.S_IRWXO) 
        alu = request.GET.get("alu",'')      
        return redirect('../atividades/'+str(alu))
    else:
        diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)
        os.system(diretorio_arquivo)    
        os.chmod(diretorio_arquivo,stat.S_IRWXO)  
        alu = request.GET.get("alu",'')      
        return redirect('../atividades/'+str(alu))

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
    if 'login' in request.POST:
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
    return render(request, 'feedback.html')

@login_required(login_url='/login')
def sair(request):
    logout(request)
    messages.success(request,"Você saiu do seu perfil")
    return HttpResponseRedirect('/login')

def turmas(request,idProfessor):
        if request.method == 'POST':
            classe = request.POST.get('classe')
            print("CLASSESESE? ",classe)
            alunos = Turmas.objects.raw("select idTurma, a.al_nome from turmas t join aluno a on t.alu_id = a.ra join Professor p on t.prof_id = idProfessor where t.classe =%s and t.prof_id = %s group by a.al_nome",(str(classe),str(idProfessor)))
            turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe",str(idProfessor))
        else:
            alunos = ""
            turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe",str(idProfessor))         
        return render(request, 'turmas.html', {'turmas': turmas,'alunos':alunos})

def enviar_arquivo(request,idProfessor):
    if 'turma' in request.POST:
        classe = request.POST.get('classe')
        classe2 = request.POST.get('classe')
        alunos = Turmas.objects.raw("select idTurma, a.al_nome from turmas t join aluno a on t.alu_id = a.ra join Professor p on t.prof_id = idProfessor where t.classe =%s and t.prof_id = %s group by a.al_nome",(str(classe),str(idProfessor)))
        turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe",str(idProfessor))        
    elif 'enviar' in request.POST:
        try:
            classe = request.POST.get('classe')
            classe2 = request.POST.get('classe')
            turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe",str(idProfessor))   
            alunos = Turmas.objects.raw("select idTurma, a.al_nome from turmas t join aluno a on t.alu_id = a.ra join Professor p on t.prof_id = idProfessor where t.classe =%s and t.prof_id = %s group by a.ra",(str(classe),str(idProfessor)))
            for a in request.POST.getlist('alu_ra'):
                arq = EnviarArquivo()
                arquivo = request.FILES['arquivo']
                arq.arquivo = arquivo
                alu = Aluno.objects.get(ra=a)
                arq.alu = alu
                arq.save()
            messages.success(request,"Arquivo enviado com sucesso")
        except (MultiValueDictKeyError,TypeError):
            messages.error(request,"Selecione um arquivo")
        except Aluno.DoesNotExist:
            messages.error(request,"Selecione um aluno")
    else:
        alunos = ""
        classe2 = ""
        turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe",str(idProfessor))         
    return render(request, 'enviar_arquivo.html', {'turmas': turmas,'alunos':alunos,'classe2':classe2})

@login_required(login_url='/login')
def pagina_aluno(request):
    return render(request,"pagina_aluno.html")

def pagina_professor(request,idProfessor):
    professor = idProfessor
    if 'turmas' in request.POST:
        return redirect("/turmas/"+str(idProfessor))
    return render(request,"telaProfessor.html")

def inserir(request):
    if 'enviar' in request.POST:
        alunos = Aluno.objects.all()
        ano_letivo = request.POST.get("ano_letivo")
        classe = request.POST.get("classe")
        professores = Professor.objects.all()      
        alu_id = Turmas.objects.values_list('alu_id',flat=True)
        al = request.POST.getlist('aluno_ra')
        print("ALU_ID: ",alu_id)
        for  c in Turmas.objects.values_list('classe',flat=True):
            if set(alu_id) == set(al) and c == classe:
                    messages.error(request, "Essa classe já está cadastrada")
                    return redirect('/inserir')
        for aluno in request.POST.getlist('aluno_ra'):
            for professor in request.POST.getlist('professor'):               
                    turmas = Turmas()
                    professor = Professor.objects.get(pk=professor)
                    turmas.prof = professor
                    aluno = Aluno.objects.get(pk=aluno)
                    turmas.alu = aluno
                    turmas.classe = classe
                    turmas.ano_letivo = ano_letivo           
                    turmas.save()
        messages.success(request,"Turma criada com sucesso")
    elif 'existente' in request.POST:   
            alunos = Aluno.objects.all()
            professores = Professor.objects.all()
            idProfessor = request.POST.get("idProfessor")
            if len(idProfessor) == 0:
                messages.error(request,"Insira o ID do professor")
            else:    
                return redirect('../editar_classe/'+str(idProfessor))            
    else:     
        professores = Professor.objects.all()
        alunos = Aluno.objects.all()
    return render(request, "inserir.html",{'alunos':alunos,'professores':professores})

def editar_classe(request,idProfessor):              
        if 'editar' in request.POST:          
            classe = request.POST.get("classe")
            classe2 = request.POST.get('classe')
            for aluno in request.POST.getlist('aluno_ra'):                       
                    turmas = Turmas()
                    professor = Professor.objects.get(pk=idProfessor)
                    turmas.prof = professor
                    aluno = Aluno.objects.get(pk=aluno)                
                    turmas.alu = aluno
                    turmas.classe = classe
                    ano = Turmas.objects.filter(classe=classe).values_list('ano_letivo',flat=True).first()
                    turmas.ano_letivo = ano                   
                    turmas.save()
            messages.success(request,"Turma criada com sucesso")
            alunos = Aluno.objects.raw("SELECT a.ra,t.prof_id,classe from aluno a left outer join turmas t on t.alu_id = a.ra where t.alu_id is NULL or classe <> %s or t.prof_id <> %s group by a.ra",[classe])
            turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe",str(idProfessor))
        elif 'atualizar' in request.POST:
            classe = request.POST.get('classe')
            classe2 = request.POST.get('classe')
            turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe",str(idProfessor))    
            alunos = Aluno.objects.raw("SELECT a.ra,t.prof_id,classe from aluno a left outer join turmas t on t.alu_id = a.ra where t.alu_id is NULL or classe <> %s or t.prof_id <> %s group by a.ra",[classe,idProfessor])
        else:
            alunos = ""
            turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe",str(idProfessor))
            classe2 = ""
        return render(request, "editar_classe.html",{'alunos':alunos,'turmas':turmas,'classe2':classe2})
