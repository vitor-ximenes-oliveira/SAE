import os
import stat
import subprocess as sp
from audioop import reverse
from stat import S_IREAD
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import NoReverseMatch, reverse
from django.utils.datastructures import MultiValueDictKeyError
from SAE import settings
from SAE.settings import BASE_DIR, MEDIA_ROOT
from website.models import (Aluno, EnviarArquivo, Feedback, Formulario,
                            Professor, RespostasFormulario, Turmas,
                            acertosErros, questoesEscolhidasAluno)


def cadastro_aluno(request):
    if 'CriaConta' in request.POST:
        try:
                al_email = request.POST.get("al_email")
                checar_email = Aluno.objects.get(al_email = al_email)
                if checar_email:
                    messages.error(request, "Já existe um aluno cadastrado com esse e-mail")          
        except (Aluno.DoesNotExist):
                    al_email = request.POST.get("al_email")
                    al_nascimento = request.POST.get("al_nascimento") 
                    al_nome = request.POST.get("al_nome")
                    senha = request.POST.get("al_senha")            
                    confir_senha = request.POST.get("confir_senha")
                    try:
                        if senha != confir_senha:
                            messages.error(request,"As senhas inseridas são diferentes")
                            return redirect("/Teladecadastroaluno")
                        else:
                            al_senha = make_password(senha)
                            autenticar_usuario = User(username=al_nome, password=al_senha)                          
                            autenticar_usuario.save()       
                            user = Aluno.objects.create(al_nome=al_nome, al_email=al_email,al_nascimento=al_nascimento,al_senha=al_senha)
                            user.save()            
                            messages.success(request,"Conta criada com sucesso")                      
                            return redirect('login')
                    except (ValueError,ValidationError):
                        messages.error(request, "Data de nascimento inválida")  
                    except AttributeError:
                        messages.error(request,"Preencha os campos com dados válidos")
                    except (IntegrityError):
                        messages.error(request,"Já existe um usuário cadastrado com esse nome")
        except (Aluno.MultipleObjectsReturned,User.MultipleObjectsReturned):  
                messages.error(request,"Preencha todos os campos") 
                    
    elif 'voltar' in request.POST:
            al_nome = request.POST.get("")
            al_email = request.POST.get("")
            return redirect("login")   
    return render(request,'Teladecadastroaluno.html')

def login_user(request):      
            if 'login' in request.POST:        
                    al_nome = request.POST.get("nome")
                    al_senha = request.POST.get("senha")

                    if not al_nome or not al_senha:
                        messages.error(request, "Preencha todos os campos")
                        return redirect('login')     
                    try:    
                            al_nome = request.POST.get("nome")
                            al_senha = request.POST.get("senha")    
                            aluno = Aluno.objects.get(al_nome=al_nome)            
                            usuario = User.objects.get(username=al_nome)
                            
                            if aluno:
                                checar_senha=check_password(al_senha, usuario.password)
                                if checar_senha:
                                    autenticar_usuario = authenticate(username=al_nome, password=al_senha, backend= 'django.contrib.auth.backends.AllowAllUsersModelBackend')                    
                                    login(request, autenticar_usuario)
                                    return redirect('telaAluno/'+str(aluno.ra)) 

                    except(Aluno.DoesNotExist,User.DoesNotExist):
                        try:
                                al_nome = request.POST.get("nome")
                                al_senha = request.POST.get("senha")
                                usuario = User.objects.get(username=al_nome)
                                nome_professor = usuario.username
                                adicionar_nome= Professor.objects.filter(Usuario=usuario.id).update(Nome=nome_professor)
                                professor = Professor.objects.get(Nome=usuario)
                                if professor:
                                    checar_senha=check_password(al_senha, usuario.password)
                                    if checar_senha:
                                        autenticar_usuario = authenticate(username=al_nome, password=al_senha, backend= 'django.contrib.auth.backends.AllowAllUsersModelBackend')                    
                                        login(request, autenticar_usuario)
                                        return redirect('telaProfessor/'+str(professor.idProfessor)) 
                        except(Professor.DoesNotExist,User.DoesNotExist):
                            messages.error(request,"Nome de usuário ou/e senha inválido(s)")

            elif 'cadastro' in request.POST:
                return redirect('/Teladecadastroaluno')
            return render(request,"Login.html")

def atividades(request, ra):
    material_aluno = EnviarArquivo.objects.filter(alu=ra)
    return render(request,'atividades.html',{'material_aluno':material_aluno,'ra':ra})

def visualizar_arquivo(request,arquivo):
    try:
        extensoes = [".pdf", ".txt", ".png", ".jpg", ".gif", ".bmp",".mp3",".mp4",'.JPG']
        if arquivo.endswith(tuple(extensoes)):
            diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)
            arquivo = open(diretorio_arquivo, 'rb') 
            abrir_Arquivo = FileResponse(arquivo)
            return abrir_Arquivo
        elif arquivo.endswith('.docx'): 
            diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)        
            sp.Popen(["C:\Program Files\Windows NT\Accessories\WordPad.exe", diretorio_arquivo])
            os.chmod(diretorio_arquivo,stat.S_IWUSR and stat.S_IRUSR and stat.S_IRUSR)  
            fk_aluno = request.GET.get("alu",'')      
            return redirect('../atividades/'+str(fk_aluno))
        else:
            diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)
            os.system(diretorio_arquivo)    
            os.chmod(diretorio_arquivo,S_IREAD)  
            fk_aluno = request.GET.get("alu",'')      
            return redirect('../atividades/'+str(fk_aluno))
    except(FileNotFoundError,ValueError):
            messages.error(request,"Arquivo não encontrado")
            fk_aluno = request.GET.get("alu",'')      
            return redirect('../atividades/'+str(fk_aluno))

def baixar_arquivo(request, arquivo):
    try:
        if arquivo != '':
            diretorio_arquivo = (os.path.join(settings.MEDIA_ROOT, arquivo))
            diretorio = open(diretorio_arquivo,'rb')
            download_arquivo = HttpResponse(diretorio ,content_type="aplicacao/arquivo")
            download_arquivo ['Content-Disposition'] = "attachment; nome_arquivo=" + arquivo
            return download_arquivo
        else:
            messages.error(request,"Arquivo não encontrado")
            return redirect('../atividades/'+str(fk_aluno))
    except(FileNotFoundError,ValueError):
            messages.error(request,"Arquivo não encontrado")
            fk_aluno = request.GET.get("alu",'')      
            return redirect('../atividades/'+str(fk_aluno))
    
#@login_required(login_url='/login')
def feedback(request,ra):
    if 'Log out' in request.POST:
        sair(request)
        return redirect("login")
    if request.method == 'POST':
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
            idProf = request.POST.get("professor")
            try:
                feed = Feedback()
                idProf = request.POST.get("professor")
                chaverofessor = Professor.objects.get(pk=idProf)
                feed.idProf = chaverofessor
                chaverofessor = feed.idProf
                feedback = Feedback.objects.create(pergunta1=pergunta1,justificativa1=justificativa1,pergunta2=pergunta2,justificativa2=justificativa2,pergunta3=pergunta3,justificativa3=justificativa3,pergunta4=pergunta4,justificativa4=justificativa4,pergunta5=pergunta5,justificativa5=justificativa5,pergunta6=pergunta6,justificativa6=justificativa6,pergunta7=pergunta7,justificativa7=justificativa7,pergunta8=pergunta8,justificativa8=justificativa8,pergunta9=pergunta9,justificativa9=justificativa9,idProf=chaverofessor)
                messages.success(request,"Feedback enviado com sucesso")
            except (IntegrityError,Professor.DoesNotExist):
                messages.error(request,"Escolha um professor")           
            return redirect("../feedback/"+str(ra))
    else:
        
            idProfessor = Turmas.objects.filter(alu=ra).values_list("prof_id",flat=True).first()
            professores = Professor.objects.raw("Select idProfessor,nome from professor p join turmas t join aluno a where t.prof_id=%s and t.alu_id=%s group by alu_id",[idProfessor,ra])
    return render(request, 'feedback.html',{'professores':professores,'ra':ra})

def sair(request):
        logout(request)
        messages.success(request,"Você saiu do seu perfil")
        return HttpResponseRedirect("/")

def enviar_arquivo(request,idProfessor):
    if 'Log out' in request.POST:
        sair(request)
        return redirect("login")
    if 'atualizar' in request.POST:
        classe_ano_letivo = request.POST.get('ano_letivo_classe')
        ano_letivo = classe_ano_letivo.split("|")[-2]
        classe = classe_ano_letivo.split("|")[-1]    
        alunos = Aluno.objects.raw("select a.ra,t.ano_letivo,t.prof_id,classe,alu_id,a.al_nome from aluno a join turmas t on t.alu_id = a.ra where classe = %s and ano_letivo=%s and prof_id=%s group by alu_id",[classe,ano_letivo,idProfessor])
        turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe,ano_letivo",str(idProfessor))     
        nivelDoAlunos = acertosErros.objects.raw("select ae.id, ae.nivelDoAluno,ae.aluno_id from website_acertoserros ae join turmas t on t.alu_id = ae.aluno_id join aluno a on ae.aluno_id = a.ra where classe =%s and ano_letivo=%s and prof_id=%s group by alu_id",[classe,ano_letivo,idProfessor])

    elif 'enviar' in request.POST:
        try:
            classe_ano_letivo = request.POST.get('ano_letivo_classe')
            ano_letivo = classe_ano_letivo.split("|")[-2]
            classe = classe_ano_letivo.split("|")[-1]          
            turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe,ano_letivo",str(idProfessor))   
            alunos = Aluno.objects.raw("select a.ra,t.ano_letivo,t.prof_id,classe,alu_id,a.al_nome from aluno a join turmas t on t.alu_id = a.ra where classe = %s and ano_letivo=%s and prof_id=%s group by alu_id",[classe,ano_letivo,idProfessor])
            nivelDoAlunos = acertosErros.objects.raw("select ae.id, ae.nivelDoAluno,ae.aluno_id from website_acertoserros ae join turmas t on t.alu_id = ae.aluno_id join aluno a on ae.aluno_id = a.ra where classe =%s and ano_letivo=%s and prof_id=%s group by alu_id",[classe,ano_letivo,idProfessor])
            alunos_ra = request.POST.getlist('ra')
            if not alunos_ra:
                messages.error(request,"Selecione um aluno")
                return redirect('enviar_arquivo',idProfessor)
            for alu_ra in alunos_ra:
                arq = EnviarArquivo()
                arquivo = request.FILES['arquivo']
                arq.arquivo = arquivo
                alu = Aluno.objects.get(pk=alu_ra)
                arq.alu = alu
                arq.save()
            messages.success(request,"Arquivo enviado com sucesso")
        except (MultiValueDictKeyError,TypeError):
            messages.error(request,"Selecione um arquivo")
    else:
        alunos = ""
        classe = ""
        ano_letivo = ""
        nivelDoAlunos = ""
        turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe,ano_letivo",str(idProfessor))         
    return render(request, 'enviar_arquivo.html', {'turmas': turmas,'alunos':alunos,'classe':classe,'ano_letivo':ano_letivo,'idProfessor':idProfessor,'nivelDoAlunos':nivelDoAlunos})


def telaAluno(request,ra):
    acertos = acertosErros.objects.filter(aluno=ra).values_list("acertos",flat=True).first()
    erros = acertosErros.objects.filter(aluno=ra).values_list("erros",flat=True).first()
    nivelDoAluno = acertosErros.objects.filter(aluno=ra).values_list("nivelDoAluno",flat=True).first()

    if 'feedback' in request.POST:
        return redirect("/feedback/"+str(ra))
    elif 'Log out' in request.POST:
        sair(request)
        return redirect("login")
    elif 'atividades' in request.POST:
        return redirect('atividades',ra)
    elif 'formularioAluno' in request.POST:
        return redirect('/formularioAluno/'+str(ra))
    return render(request,"telaAluno.html",{"acertos":acertos,"erros":erros,"nivelDoAluno": nivelDoAluno})

def pagina_professor(request,idProfessor):
    if 'turmas' in request.POST:
        return redirect("/turmas/"+str(idProfessor))
    elif 'Log out' in request.POST:
        sair(request)
        return redirect("login")
    elif 'criarFormulario' in request.POST:
        return redirect("../criarFormulario/"+str(idProfessor))
    elif 'graficosFeedback' in request.POST:
        return redirect("graficosFeedback",idProfessor)
    elif 'inserir_classe' in request.POST:
        return redirect("inserirTurma",idProfessor)
    elif 'enviar_arquivo' in request.POST:
        return redirect("/enviar_arquivo/"+str(idProfessor))

    return render(request,"telaProfessor.html",{"idProfessor":idProfessor})

def inserirTurma(request,idProfessor):
    if 'voltar' in request.POST:
        return redirect("../telaProfessor/"+str(idProfessor))
    if 'Log out' in request.POST:
        sair(request)
        return redirect('login')
    if 'enviar' in request.POST:

        try:
            alunos = Aluno.objects.all()
            ano_letivo = request.POST.get("ano_letivo")
            classe = request.POST.get("classe")
            professores = Professor.objects.all()
            pkProfessor = request.POST.get("professor")
            profi = Turmas.objects.filter(prof=pkProfessor).values_list('prof_id',flat=True).first()
            nova_turma = Turmas.objects.get(ano_letivo=ano_letivo,classe=classe,prof=profi)
            if pkProfessor is None:
                messages.error(request,"Selecione um professor")
                return redirect('../inserirTurma/'+str(idProfessor))
        except Turmas.MultipleObjectsReturned:         
                messages.error(request,"Já existe uma turma com essas informações")
                return redirect('../inserirTurma/'+str(idProfessor))
        except Turmas.DoesNotExist:
            if request.POST.get("classe") and request.POST.get("ano_letivo"):
                alunos_selecionados = request.POST.getlist('aluno_ra')
                if pkProfessor is None or not alunos_selecionados or not ano_letivo:
                        messages.error(request,"Preencha todos os campos da opção que deseja executar")
                        return redirect("../inserirTurma/"+str(idProfessor))
                for aluno in alunos_selecionados:
                    for professor in request.POST.getlist('professor'):              
                            turmas = Turmas()
                            id_professor = Professor.objects.get(pk=professor)
                            turmas.prof = id_professor
                            id_aluno = Aluno.objects.get(pk=aluno)
                            turmas.alu = id_aluno
                            turmas.classe = classe
                            turmas.ano_letivo = ano_letivo           
                            turmas.save()
                messages.success(request,"Turma criada com sucesso")
            else:
             
                messages.error(request,"Preencha todos os campos da opção que deseja executar")
                return redirect("../inserirTurma/"+str(idProfessor))  
        turmas = Turmas.objects.raw("SELECT * from turmas t join professor p on t.prof_id = p.idProfessor group by classe,prof_id,ano_letivo")  
    elif 'classe_existente' in request.POST:
        alunos = Aluno.objects.all()
        professores = Professor.objects.all()
        turmas = Turmas.objects.raw("SELECT * from turmas t join professor p on t.prof_id = p.idProfessor group by classe,prof_id,ano_letivo")  
        try:   
            if request.POST.get("idProfessor"):
                pkProfessor = request.POST.get("idProfessor")   
                for prof_id in Professor.objects.values_list("idProfessor",flat=True):
                    if str(prof_id) == str(pkProfessor):    
                        return redirect(reverse('editarTurma',args=[pkProfessor]))
                messages.error(request,"ID inválido")
                return redirect("../inserirTurma/"+str(idProfessor))
            else:    
                messages.error(request,"Insira o ID do professor")
                return redirect("../inserirTurma/"+str(idProfessor))
        except ValueError:
                    messages.error(request,"Não existe um professor com esse ID")
                    return redirect("../inserirTurma/"+str(idProfessor))
        except NoReverseMatch:
            messages.error(request,"Insira um ID que seja válido")
            return redirect("../inserirTurma/"+str(idProfessor))
    else:     
        professores = Professor.objects.all()
        alunos = Aluno.objects.all()
        turmas = Turmas.objects.raw("SELECT * from turmas t join professor p on t.prof_id = p.idProfessor group by classe,prof_id,ano_letivo")  
    return render(request, "inserirTurma.html",{'alunos':alunos,'professores':professores,'turmas':turmas,'idProfessor':idProfessor})

def editarTurma(request,idProfessor):
        if 'voltar' in request.POST:
            return redirect("../inserirTurma/"+(idProfessor))             
        if 'editar' in request.POST:
            try:
                classe_ano_letivo = request.POST.get('ano_letivo_classe')
                ano_letivo = classe_ano_letivo.split("|")[-2]
                classe = classe_ano_letivo.split("|")[-1]
                alunos = request.POST.getlist('aluno_ra')
                
            except UnboundLocalError:
                messages.error("Selecione um aluno")
                return redirect('editarTurma',idProfessor)
            if not alunos:
                messages.error(request,"Selecione um aluno")
                return redirect('editarTurma',idProfessor)
            for aluno in alunos:                        
                    turmas = Turmas()
                    id_professor = Professor.objects.get(pk=idProfessor)
                    turmas.prof = id_professor
                    id_aluno = Aluno.objects.get(pk=aluno)                
                    turmas.alu = id_aluno
                    turmas.classe = classe
                    turmas.ano_letivo = ano_letivo                    
                    turmas.save()
            messages.success(request,"Turma atualizada com sucesso")            
            alunos = Aluno.objects.raw("select a.ra,t.ano_letivo,t.prof_id,classe,alu_id,a.al_nome from aluno a left outer join turmas t on t.alu_id = a.ra where alu_id not in (select alu_id from turmas where classe = %s and ano_letivo=%s and prof_id=%s or prof_id<>NULL) group by alu_id",[classe,ano_letivo,idProfessor])
            turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe,ano_letivo",str(idProfessor))
            return redirect("../editarTurma/"+str(idProfessor))
        elif 'atualizar' in request.POST:
            classe_ano_letivo = request.POST.get('ano_letivo_classe')
            ano_letivo = classe_ano_letivo.split("|")[-2]
            classe = classe_ano_letivo.split("|")[-1]
            turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe,ano_letivo",str(idProfessor))  

            alunos = Aluno.objects.raw("select a.ra,t.ano_letivo,t.prof_id,classe,alu_id,a.al_nome from aluno a left outer join turmas t on t.alu_id = a.ra where a.ra not in (select alu_id from turmas where classe = %s and ano_letivo=%s and prof_id=%s or t.prof_id<>NULL) group by alu_id",[classe,ano_letivo,idProfessor])
        else:
            alunos = ""
            classe=""
            ano_letivo = ""
            turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe,ano_letivo",[idProfessor])
        return render(request, "editarTurma.html",{'alunos':alunos,'turmas':turmas,'ano_letivo':ano_letivo,'classe':classe})

def graficosFeedback(request,idProfessor):
    if 'Log out' in request.POST:
        sair(request)
        return redirect("login")
    if 'voltar' in request.POST:
        return redirect("../telaProfessor/"+str(idProfessor))
    else:  
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

        pergunta1 = Feedback.objects.filter(idProf=idProfessor).values_list("pergunta1", flat=True)

        for x in pergunta1:
            if(x == 'Ruim'):
                ruim+=1
                
            elif(x == 'Bom'):
                bom+=1
            elif(x == 'Ótimo'):
                medio+=1
            else:
                excelente+=1


        pergunta2 = Feedback.objects.filter(idProf=idProfessor).values_list("pergunta2", flat=True)

        for x in pergunta2:
            if(x == 'Ruim'):
                ruim2+=1
            elif(x == 'Bom'):
                bom2+=1
            elif(x == 'Ótimo'):
                medio2+=1
            else:
                excelente2+=1

        pergunta3 = Feedback.objects.filter(idProf=idProfessor).values_list("pergunta3", flat=True)

        for x in pergunta3:
            if(x == 'Ruim'):
                ruim3+=1
            elif(x == 'Bom'):
                bom3+=1
            elif(x == 'Ótimo'):
                medio3+=1
            else:
                excelente3+=1

        pergunta4 = Feedback.objects.filter(idProf=idProfessor).values_list("pergunta4", flat=True)

        for x in pergunta4:
            if(x == 'Ruim'):
                ruim4+=1
            elif(x == 'Bom'):
                bom4+=1
            elif(x == 'Ótimo'):
                medio4+=1
            else:
                excelente4+=1

        pergunta5 = Feedback.objects.filter(idProf=idProfessor).values_list("pergunta5", flat=True)

        for x in pergunta5:
            if(x == 'Ruim'):
                ruim5+=1
            elif(x == 'Bom'):
                bom5+=1
            elif(x == 'Ótimo'):
                medio5+=1
            else:
                excelente5+=1

        pergunta6 = Feedback.objects.filter(idProf=idProfessor).values_list("pergunta6", flat=True)

        for x in pergunta6:
            if(x == 'Ruim'):
                ruim6+=1
            elif(x == 'Bom'):
                bom6+=1
            elif(x == 'Ótimo'):
                medio6+=1
            else:
                excelente6+=1

        pergunta7 = Feedback.objects.filter(idProf=idProfessor).values_list("pergunta7", flat=True)

        for x in pergunta7:
            if(x == 'Ruim'):
                ruim7+=1
            elif(x == 'Bom'):
                bom7+=1
            elif(x == 'Ótimo'):
                medio7+=1
            else:
                excelente7+=1

        pergunta8 = Feedback.objects.filter(idProf=idProfessor).values_list("pergunta8", flat=True)

        for x in pergunta8:
            if(x == 'Ruim'):
                ruim8+=1
            elif(x == 'Bom'):
                bom8+=1
            elif(x == 'Ótimo'):
                medio8+=1
            else:
                excelente8+=1

        pergunta9 = Feedback.objects.filter(idProf=idProfessor).values_list("pergunta9", flat=True)

        for x in pergunta9:
            if(x == 'Ruim'):
                ruim9+=1
            elif(x == 'Bom'):
                bom9+=1
            elif(x == 'Ótimo'):
                medio9+=1
            else:
                excelente9+=1


    for x in pergunta9:
        if(x == 'Ruim'):
            ruim9+=1
        elif(x == 'Bom'):
            bom9+=1
        elif(x == 'Ótimo'):
            medio9+=1
        else:
            excelente9+=1       
        
        
            
    return render(request, "graficosFeedback.html" , {"idProfessor":idProfessor,"ruim" : ruim, "bom" : bom, "medio" : medio , "excelente": excelente, "ruim2" : ruim2, "bom2" : bom2, "medio2" : medio2 , "excelente2": excelente2, "ruim3" : ruim3, "bom3" : bom3, "medio3" : medio3 , "excelente3": excelente3, "ruim4" : ruim4, "bom4" : bom4, "medio4" : medio4 , "excelente4": excelente4, "ruim5" : ruim5, "bom5" : bom5, "medio5" : medio5 , "excelente5": excelente5, "ruim6" : ruim6, "bom6" : bom6, "medio6" : medio6 , "excelente6": excelente6, "ruim7" : ruim7, "bom7" : bom7, "medio7" : medio7 , "excelente7": excelente7, "ruim8" : ruim8, "bom8" : bom8, "medio8" : medio8 , "excelente8": excelente8, "ruim9" : ruim9, "bom9" : bom9, "medio9" : medio9 , "excelente9": excelente9})

def criarFormulario(request,idProfessor):
    if 'Log out' in request.POST:
        sair(request)
        return redirect("login")
    if 'formulario' in request.POST:
    
            questao1 = request.POST.get("txtQuestao")
            alternativaAquestao1 =  request.POST.get("txtAltA1")
            alternativaBquestao1 =  request.POST.get("txtAltB1")
            alternativaCquestao1 =  request.POST.get("txtAltC1")
            alternativaDquestao1 =  request.POST.get("txtAltD1")
            questao2 = request.POST.get("txtQuestao2")
            alternativaAquestao2 =  request.POST.get("txtAltA2")
            alternativaBquestao2 =  request.POST.get("txtAltB2")
            alternativaCquestao2 =  request.POST.get("txtAltC2")
            alternativaDquestao2 =  request.POST.get("txtAltD2")
            questao3 = request.POST.get("txtQuestao3")
            alternativaAquestao3 =  request.POST.get("txtAltA3")
            alternativaBquestao3 =  request.POST.get("txtAltB3")
            alternativaCquestao3 =  request.POST.get("txtAltC3")
            alternativaDquestao3 =  request.POST.get("txtAltD3")
            questao4 = request.POST.get("txtQuestao4")
            alternativaAquestao4 =  request.POST.get("txtAltA4")
            alternativaBquestao4 =  request.POST.get("txtAltB4")
            alternativaCquestao4 =  request.POST.get("txtAltC4")
            alternativaDquestao4 =  request.POST.get("txtAltD4")
            questao5 = request.POST.get("txtQuestao5")
            alternativaAquestao5 =  request.POST.get("txtAltA5")
            alternativaBquestao5 =  request.POST.get("txtAltB5")
            alternativaCquestao5 =  request.POST.get("txtAltC5")
            alternativaDquestao5 =  request.POST.get("txtAltD5")
            questao6 = request.POST.get("txtQuestao6")
            alternativaAquestao6 =  request.POST.get("txtAltA6")
            alternativaBquestao6 =  request.POST.get("txtAltB6")
            alternativaCquestao6 =  request.POST.get("txtAltC6")
            alternativaDquestao6 =  request.POST.get("txtAltD6")
            questao7 = request.POST.get("txtQuestao7")
            alternativaAquestao7 =  request.POST.get("txtAltA7")
            alternativaBquestao7 =  request.POST.get("txtAltB7")
            alternativaCquestao7 =  request.POST.get("txtAltC7")
            alternativaDquestao7 =  request.POST.get("txtAltD7")
            questao8 = request.POST.get("txtQuestao8")
            alternativaAquestao8 =  request.POST.get("txtAltA8")
            alternativaBquestao8 =  request.POST.get("txtAltB8")
            alternativaCquestao8 =  request.POST.get("txtAltC8")
            alternativaDquestao8 =  request.POST.get("txtAltD8")
            questao9 = request.POST.get("txtQuestao9")
            alternativaAquestao9 =  request.POST.get("txtAltA9")
            alternativaBquestao9 =  request.POST.get("txtAltB9")
            alternativaCquestao9 =  request.POST.get("txtAltC9")
            alternativaDquestao9 =  request.POST.get("txtAltD9")
            questao10 = request.POST.get("txtQuestao10")
            alternativaAquestao10 =  request.POST.get("txtAltA10")
            alternativaBquestao10 =  request.POST.get("txtAltB10")
            alternativaCquestao10 =  request.POST.get("txtAltC10")
            alternativaDquestao10 =  request.POST.get("txtAltD10")
            formulario = Formulario.objects.create(questao1=questao1, alternativaAquestao1=alternativaAquestao1,alternativaBquestao1=alternativaBquestao1,alternativaCquestao1=alternativaCquestao1,alternativaDquestao1=alternativaDquestao1,questao2=questao2, alternativaAquestao2=alternativaAquestao2,alternativaBquestao2=alternativaBquestao2,alternativaCquestao2=alternativaCquestao2,alternativaDquestao2=alternativaDquestao2,questao3=questao3, alternativaAquestao3=alternativaAquestao3,alternativaBquestao3=alternativaBquestao3,alternativaCquestao3=alternativaCquestao3,alternativaDquestao3=alternativaDquestao3,questao4=questao4, alternativaAquestao4=alternativaAquestao4,alternativaBquestao4=alternativaBquestao4,alternativaCquestao4=alternativaCquestao4,alternativaDquestao4=alternativaDquestao4,questao5=questao5, alternativaAquestao5=alternativaAquestao5,alternativaBquestao5=alternativaBquestao5,alternativaCquestao5=alternativaCquestao5,alternativaDquestao5=alternativaDquestao5,questao6=questao6, alternativaAquestao6=alternativaAquestao6,alternativaBquestao6=alternativaBquestao6,alternativaCquestao6=alternativaCquestao6,alternativaDquestao6=alternativaDquestao6,questao7=questao7, alternativaAquestao7=alternativaAquestao7,alternativaBquestao7=alternativaBquestao7,alternativaCquestao7=alternativaCquestao7,alternativaDquestao7=alternativaDquestao7,questao8=questao8, alternativaAquestao8=alternativaAquestao8,alternativaBquestao8=alternativaBquestao8,alternativaCquestao8=alternativaCquestao8,alternativaDquestao8=alternativaDquestao8,questao9=questao9, alternativaAquestao9=alternativaAquestao9,alternativaBquestao9=alternativaBquestao9,alternativaCquestao9=alternativaCquestao9,alternativaDquestao9=alternativaDquestao9,questao10=questao10, alternativaAquestao10=alternativaAquestao10,alternativaBquestao10=alternativaBquestao10,alternativaCquestao10=alternativaCquestao10,alternativaDquestao10=alternativaDquestao10)
            messages.success(request,"Formulario criado com sucesso")           
            return redirect("../gabaritoFormulario/"+str(idProfessor))
      
    return render(request, 'criarFormulario.html',{"idProfessor":idProfessor})

def gabaritoFormulario(request,idProfessor):
        if 'Log out' in request.POST:
            sair(request)
            return redirect("login")
        questao1 = Formulario.objects.values_list("questao1",flat=True).last()
        alternativaAquestao1 = Formulario.objects.values_list("alternativaAquestao1",flat=True).last()
        alternativaBquestao1 = Formulario.objects.values_list("alternativaBquestao1",flat=True).last()
        alternativaCquestao1 = Formulario.objects.values_list("alternativaCquestao1",flat=True).last()
        alternativaDquestao1 = Formulario.objects.values_list("alternativaDquestao1",flat=True).last()
        questao2 = Formulario.objects.values_list("questao2",flat=True).last()
        alternativaAquestao2 = Formulario.objects.values_list("alternativaAquestao2",flat=True).last()
        alternativaBquestao2 = Formulario.objects.values_list("alternativaBquestao2",flat=True).last()
        alternativaCquestao2 = Formulario.objects.values_list("alternativaCquestao2",flat=True).last()
        alternativaDquestao2 = Formulario.objects.values_list("alternativaDquestao2",flat=True).last()
        questao3 = Formulario.objects.values_list("questao3",flat=True).last()
        alternativaAquestao3 = Formulario.objects.values_list("alternativaAquestao3",flat=True).last()
        alternativaBquestao3 = Formulario.objects.values_list("alternativaBquestao3",flat=True).last()
        alternativaCquestao3 = Formulario.objects.values_list("alternativaCquestao3",flat=True).last()
        alternativaDquestao3 = Formulario.objects.values_list("alternativaDquestao3",flat=True).last()
        questao4 = Formulario.objects.values_list("questao4",flat=True).last()
        alternativaAquestao4 = Formulario.objects.values_list("alternativaAquestao4",flat=True).last()
        alternativaBquestao4 = Formulario.objects.values_list("alternativaBquestao4",flat=True).last()
        alternativaCquestao4 = Formulario.objects.values_list("alternativaCquestao4",flat=True).last()
        alternativaDquestao4 = Formulario.objects.values_list("alternativaDquestao4",flat=True).last()
        questao5 = Formulario.objects.values_list("questao5",flat=True).last()
        alternativaAquestao5 = Formulario.objects.values_list("alternativaAquestao5",flat=True).last()
        alternativaBquestao5 = Formulario.objects.values_list("alternativaBquestao5",flat=True).last()
        alternativaCquestao5 = Formulario.objects.values_list("alternativaCquestao5",flat=True).last()
        alternativaDquestao5 = Formulario.objects.values_list("alternativaDquestao5",flat=True).last()
        questao6 = Formulario.objects.values_list("questao6",flat=True).last()
        alternativaAquestao6 = Formulario.objects.values_list("alternativaAquestao6",flat=True).last()
        alternativaBquestao6 = Formulario.objects.values_list("alternativaBquestao6",flat=True).last()
        alternativaCquestao6 = Formulario.objects.values_list("alternativaCquestao6",flat=True).last()
        alternativaDquestao6 = Formulario.objects.values_list("alternativaDquestao6",flat=True).last()
        questao7 = Formulario.objects.values_list("questao7",flat=True).last()
        alternativaAquestao7 = Formulario.objects.values_list("alternativaAquestao7",flat=True).last()
        alternativaBquestao7 = Formulario.objects.values_list("alternativaBquestao7",flat=True).last()
        alternativaCquestao7 = Formulario.objects.values_list("alternativaCquestao7",flat=True).last()
        alternativaDquestao7 = Formulario.objects.values_list("alternativaDquestao7",flat=True).last()
        questao8 = Formulario.objects.values_list("questao8",flat=True).last()
        alternativaAquestao8 = Formulario.objects.values_list("alternativaAquestao8",flat=True).last()
        alternativaBquestao8 = Formulario.objects.values_list("alternativaBquestao8",flat=True).last()
        alternativaCquestao8 = Formulario.objects.values_list("alternativaCquestao8",flat=True).last()
        alternativaDquestao8 = Formulario.objects.values_list("alternativaDquestao8",flat=True).last()
        questao9 = Formulario.objects.values_list("questao9",flat=True).last()
        alternativaAquestao9 = Formulario.objects.values_list("alternativaAquestao9",flat=True).last()
        alternativaBquestao9 = Formulario.objects.values_list("alternativaBquestao9",flat=True).last()
        alternativaCquestao9 = Formulario.objects.values_list("alternativaCquestao9",flat=True).last()
        alternativaDquestao9 = Formulario.objects.values_list("alternativaDquestao9",flat=True).last()
        questao10 = Formulario.objects.values_list("questao10",flat=True).last()
        alternativaAquestao10 = Formulario.objects.values_list("alternativaAquestao10",flat=True).last()
        alternativaBquestao10 = Formulario.objects.values_list("alternativaBquestao10",flat=True).last()
        alternativaCquestao10 = Formulario.objects.values_list("alternativaCquestao10",flat=True).last()
        alternativaDquestao10 = Formulario.objects.values_list("alternativaDquestao10",flat=True).last()
        
        
        if 'gabarito' in request.POST:
            respostaQuestao1 = request.POST.get("btn-radio")
            respostaQuestao2 = request.POST.get("btn-radio2")
            respostaQuestao3 = request.POST.get("btn-radio3")
            respostaQuestao4 = request.POST.get("btn-radio4")
            respostaQuestao5 = request.POST.get("btn-radio5")
            respostaQuestao6 = request.POST.get("btn-radio6")
            respostaQuestao7 = request.POST.get("btn-radio7")
            respostaQuestao8 = request.POST.get("btn-radio8")
            respostaQuestao9 = request.POST.get("btn-radio9")
            respostaQuestao10 = request.POST.get("btn-radio10")
            gabarito = RespostasFormulario.objects.create(respostaQuestao1=respostaQuestao1,respostaQuestao2=respostaQuestao2,respostaQuestao3=respostaQuestao3,respostaQuestao4=respostaQuestao4,respostaQuestao5=respostaQuestao5,respostaQuestao6=respostaQuestao6,respostaQuestao7=respostaQuestao7,respostaQuestao8=respostaQuestao8,respostaQuestao9=respostaQuestao9,respostaQuestao10=respostaQuestao10)
            messages.success(request,"Gabarito enviado com sucesso")  
            return redirect("../telaProfessor/"+str(idProfessor))
            
    
        
        return render(request, "gabaritoFormulario.html", {"idProfessor":idProfessor,"questao1": questao1,"alternativaAquestao1":alternativaAquestao1, "alternativaBquestao1":alternativaBquestao1,"alternativaCquestao1":alternativaCquestao1,"alternativaDquestao1":alternativaDquestao1,"questao2":questao2,"alternativaAquestao2":alternativaAquestao2, "alternativaBquestao2":alternativaBquestao2,"alternativaCquestao2":alternativaCquestao2,"alternativaDquestao2":alternativaDquestao2,"questao3":questao3,"alternativaAquestao3":alternativaAquestao3, "alternativaBquestao3":alternativaBquestao3,"alternativaCquestao3":alternativaCquestao3,"alternativaDquestao3":alternativaDquestao3,"questao4":questao4,"alternativaAquestao4":alternativaAquestao4, "alternativaBquestao4":alternativaBquestao4,"alternativaCquestao4":alternativaCquestao4,"alternativaDquestao4":alternativaDquestao4,"questao5":questao5,"alternativaAquestao5":alternativaAquestao5, "alternativaBquestao5":alternativaBquestao5,"alternativaCquestao5":alternativaCquestao5,"alternativaDquestao5":alternativaDquestao5,"questao6":questao6,"alternativaAquestao6":alternativaAquestao6, "alternativaBquestao6":alternativaBquestao6,"alternativaCquestao6":alternativaCquestao6,"alternativaDquestao6":alternativaDquestao6,"questao7":questao7,"alternativaAquestao7":alternativaAquestao7, "alternativaBquestao7":alternativaBquestao7,"alternativaCquestao7":alternativaCquestao7,"alternativaDquestao7":alternativaDquestao7,"questao8":questao8,"alternativaAquestao8":alternativaAquestao8, "alternativaBquestao8":alternativaBquestao8,"alternativaCquestao8":alternativaCquestao8,"alternativaDquestao8":alternativaDquestao8,"questao9":questao9,"alternativaAquestao9":alternativaAquestao9, "alternativaBquestao9":alternativaBquestao9,"alternativaCquestao9":alternativaCquestao9,"alternativaDquestao9":alternativaDquestao9,"questao10":questao10,"alternativaAquestao10":alternativaAquestao10, "alternativaBquestao10":alternativaBquestao10,"alternativaCquestao10":alternativaCquestao10,"alternativaDquestao10":alternativaDquestao10})
    
def graficoAluno(request,ra):
    if 'Log out' in request.POST:
        sair(request)
        return redirect("login")
    global ninveldoAluno
    if 'responderFomulario' in request.POST:
        acertos = 0
        erros = 0
        nivelDoAluno = 0

        #respostas do aluno
        respostasAluno = []
        questao1 = RespostasFormulario.objects.values_list("respostaQuestao1",flat=True).filter(alu_id=ra)
        questao2 = RespostasFormulario.objects.values_list("respostaQuestao2",flat=True).filter(alu_id=ra)
        questao3 = RespostasFormulario.objects.values_list("respostaQuestao3",flat=True).filter(alu_id=ra)
        questao4 = RespostasFormulario.objects.values_list("respostaQuestao4",flat=True).filter(alu_id=ra)
        questao5 = RespostasFormulario.objects.values_list("respostaQuestao5",flat=True).filter(alu_id=ra)
        questao6 = RespostasFormulario.objects.values_list("respostaQuestao6",flat=True).filter(alu_id=ra)
        questao7 = RespostasFormulario.objects.values_list("respostaQuestao7",flat=True).filter(alu_id=ra)
        questao8 = RespostasFormulario.objects.values_list("respostaQuestao8",flat=True).filter(alu_id=ra)
        questao9 = RespostasFormulario.objects.values_list("respostaQuestao9",flat=True).filter(alu_id=ra)
        questao10 = Formulario.objects.values_list("respostaQuestao10",flat=True).first()

        #adicionando as respostas na lista
        respostasAluno.append(questao1)
        respostasAluno.append(questao2)
        respostasAluno.append(questao3)
        respostasAluno.append(questao4)
        respostasAluno.append(questao5)
        respostasAluno.append(questao6)
        respostasAluno.append(questao7)
        respostasAluno.append(questao8)
        respostasAluno.append(questao9)
        respostasAluno.append(questao10)

        #gabarito do professor
        respostasGabarito = []
        resposta1 = Formulario.objects.values_list("respostaQuestao1",flat=True).first()
        resposta2 = Formulario.objects.values_list("respostaQuestao2",flat=True).first()
        resposta3 = Formulario.objects.values_list("respostaQuestao3",flat=True).first()
        resposta4 = Formulario.objects.values_list("respostaQuestao4",flat=True).first()
        resposta5 = Formulario.objects.values_list("respostaQuestao5",flat=True).first()
        resposta6 = Formulario.objects.values_list("respostaQuestao6",flat=True).first()
        resposta7 = Formulario.objects.values_list("respostaQuestao7",flat=True).first()
        resposta8 = Formulario.objects.values_list("respostaQuestao8",flat=True).first()
        resposta9 = Formulario.objects.values_list("respostaQuestao9",flat=True).first()
        resposta10 = Formulario.objects.values_list("respostaQuestao10",flat=True).first()

        respostasGabarito.append(resposta1)
        respostasGabarito.append(resposta2)
        respostasGabarito.append(resposta3)
        respostasGabarito.append(resposta4)
        respostasGabarito.append(resposta5)
        respostasGabarito.append(resposta6)
        respostasGabarito.append(resposta7)
        respostasGabarito.append(resposta8)
        respostasGabarito.append(resposta9)
        respostasGabarito.append(resposta10)

        for x in range(0,10,1):
            if(respostasAluno[x] == respostasGabarito[x]):
                acertos+=1
            else:
                erros+=1
    
        if( (acertos == 0 and erros == 10) or (acertos == 1 and erros == 9) or (acertos == 2 and erros == 8) or (acertos == 3 and erros == 7) or (acertos == 4 and erros == 6)):
            nivelDoAluno = "Insuficiente"
        elif(acertos == 5 and erros == 5):
            nivelDoAluno = "Básico"
        elif((acertos == 6 and erros == 4) or (acertos == 7 and erros == 3) or (acertos == 8 and erros == 2) ):
            nivelDoAluno = "Proficiente"
        elif((acertos == 9 and erros == 1) or (acertos == 10 and erros == 0)):
            nivelDoAluno = "Avançado"
        return redirect("/telaAluno/"+str(ra))
    return render(request, "formularioAluno.html", { "erros":erros, "acertos":acertos,"ra":ra})

def formularioAluno(request,ra):
    
        global nivelDoAluno
        if 'sair' in request.POST:
            return redirect("../telaAluno/"+str(ra))
        if 'Log out' in request.POST:
            sair(request)
            return redirect("login")
        questao1 = Formulario.objects.values_list("questao1",flat=True).last()
        alternativaAquestao1 = Formulario.objects.values_list("alternativaAquestao1",flat=True).last()
        alternativaBquestao1 = Formulario.objects.values_list("alternativaBquestao1",flat=True).last()
        alternativaCquestao1 = Formulario.objects.values_list("alternativaCquestao1",flat=True).last()
        alternativaDquestao1 = Formulario.objects.values_list("alternativaDquestao1",flat=True).last()
        questao2 = Formulario.objects.values_list("questao2",flat=True).last()
        alternativaAquestao2 = Formulario.objects.values_list("alternativaAquestao2",flat=True).last()
        alternativaBquestao2 = Formulario.objects.values_list("alternativaBquestao2",flat=True).last()
        alternativaCquestao2 = Formulario.objects.values_list("alternativaCquestao2",flat=True).last()
        alternativaDquestao2 = Formulario.objects.values_list("alternativaDquestao2",flat=True).last()
        questao3 = Formulario.objects.values_list("questao3",flat=True).last()
        alternativaAquestao3 = Formulario.objects.values_list("alternativaAquestao3",flat=True).last()
        alternativaBquestao3 = Formulario.objects.values_list("alternativaBquestao3",flat=True).last()
        alternativaCquestao3 = Formulario.objects.values_list("alternativaCquestao3",flat=True).last()
        alternativaDquestao3 = Formulario.objects.values_list("alternativaDquestao3",flat=True).last()
        questao4 = Formulario.objects.values_list("questao4",flat=True).last()
        alternativaAquestao4 = Formulario.objects.values_list("alternativaAquestao4",flat=True).last()
        alternativaBquestao4 = Formulario.objects.values_list("alternativaBquestao4",flat=True).last()
        alternativaCquestao4 = Formulario.objects.values_list("alternativaCquestao4",flat=True).last()
        alternativaDquestao4 = Formulario.objects.values_list("alternativaDquestao4",flat=True).last()
        questao5 = Formulario.objects.values_list("questao5",flat=True).last()
        alternativaAquestao5 = Formulario.objects.values_list("alternativaAquestao5",flat=True).last()
        alternativaBquestao5 = Formulario.objects.values_list("alternativaBquestao5",flat=True).last()
        alternativaCquestao5 = Formulario.objects.values_list("alternativaCquestao5",flat=True).last()
        alternativaDquestao5 = Formulario.objects.values_list("alternativaDquestao5",flat=True).last()
        questao6 = Formulario.objects.values_list("questao6",flat=True).last()
        alternativaAquestao6 = Formulario.objects.values_list("alternativaAquestao6",flat=True).last()
        alternativaBquestao6 = Formulario.objects.values_list("alternativaBquestao6",flat=True).last()
        alternativaCquestao6 = Formulario.objects.values_list("alternativaCquestao6",flat=True).last()
        alternativaDquestao6 = Formulario.objects.values_list("alternativaDquestao6",flat=True).last()
        questao7 = Formulario.objects.values_list("questao7",flat=True).last()
        alternativaAquestao7 = Formulario.objects.values_list("alternativaAquestao7",flat=True).last()
        alternativaBquestao7 = Formulario.objects.values_list("alternativaBquestao7",flat=True).last()
        alternativaCquestao7 = Formulario.objects.values_list("alternativaCquestao7",flat=True).last()
        alternativaDquestao7 = Formulario.objects.values_list("alternativaDquestao7",flat=True).last()
        questao8 = Formulario.objects.values_list("questao8",flat=True).last()
        alternativaAquestao8 = Formulario.objects.values_list("alternativaAquestao8",flat=True).last()
        alternativaBquestao8 = Formulario.objects.values_list("alternativaBquestao8",flat=True).last()
        alternativaCquestao8 = Formulario.objects.values_list("alternativaCquestao8",flat=True).last()
        alternativaDquestao8 = Formulario.objects.values_list("alternativaDquestao8",flat=True).last()
        questao9 = Formulario.objects.values_list("questao9",flat=True).last()
        alternativaAquestao9 = Formulario.objects.values_list("alternativaAquestao9",flat=True).last()
        alternativaBquestao9 = Formulario.objects.values_list("alternativaBquestao9",flat=True).last()
        alternativaCquestao9 = Formulario.objects.values_list("alternativaCquestao9",flat=True).last()
        alternativaDquestao9 = Formulario.objects.values_list("alternativaDquestao9",flat=True).last()
        questao10 = Formulario.objects.values_list("questao10",flat=True).last()
        alternativaAquestao10 = Formulario.objects.values_list("alternativaAquestao10",flat=True).last()
        alternativaBquestao10 = Formulario.objects.values_list("alternativaBquestao10",flat=True).last()
        alternativaCquestao10 = Formulario.objects.values_list("alternativaCquestao10",flat=True).last()
        alternativaDquestao10 = Formulario.objects.values_list("alternativaDquestao10",flat=True).last()

        if 'responderFomulario' in request.POST:   
            respostaQuestao1 = request.POST.get("btn-radio")
            respostaQuestao2 = request.POST.get("btn-radio2")
            respostaQuestao3 = request.POST.get("btn-radio3")
            respostaQuestao4 = request.POST.get("btn-radio4")
            respostaQuestao5 = request.POST.get("btn-radio5")
            respostaQuestao6 = request.POST.get("btn-radio6")
            respostaQuestao7 = request.POST.get("btn-radio7")
            respostaQuestao8 = request.POST.get("btn-radio8")
            respostaQuestao9 = request.POST.get("btn-radio9")
            respostaQuestao10 = request.POST.get("btn-radio10")
            questoesEscolhidasAluno.objects.create(respostaQuestao1=respostaQuestao1,respostaQuestao2=respostaQuestao2,respostaQuestao3=respostaQuestao3,respostaQuestao4=respostaQuestao4,respostaQuestao5=respostaQuestao5,respostaQuestao6=respostaQuestao6,respostaQuestao7=respostaQuestao7,respostaQuestao8=respostaQuestao8,respostaQuestao9=respostaQuestao9,respostaQuestao10=respostaQuestao10)
           
            acertosAluno=0
            errosAluno=0
            nivelDoAluno = ""
    
            if(alternativaAquestao1==respostaQuestao1):
                    acertosAluno = acertosAluno+1
            else:
                    errosAluno = errosAluno+1
            if(alternativaAquestao2==respostaQuestao2):
                    acertosAluno = acertosAluno+1
            else:
                    errosAluno = errosAluno+1
            if(alternativaAquestao3==respostaQuestao3):
                    acertosAluno = acertosAluno+1
            else:
                    errosAluno = errosAluno+1
            if(alternativaAquestao4==respostaQuestao4):
                    acertosAluno = acertosAluno+1
            else:
                    errosAluno = errosAluno+1
            if(alternativaAquestao5==respostaQuestao5):
                    acertosAluno = acertosAluno+1
            else:
                    errosAluno = errosAluno+1
            if(alternativaAquestao6==respostaQuestao6):
                    acertosAluno = acertosAluno+1
            else:
                    errosAluno = errosAluno+1
            if(alternativaAquestao7==respostaQuestao7):
                    acertosAluno = acertosAluno+1
            else:
                    errosAluno = errosAluno+1
            if(alternativaAquestao8==respostaQuestao8):
                    acertosAluno = acertosAluno+1
            else:
                    errosAluno = errosAluno+1
            if(alternativaAquestao9==respostaQuestao9):
                    acertosAluno = acertosAluno+1
            else:
                    errosAluno = errosAluno+1
            if(alternativaAquestao10==respostaQuestao10):
                    acertosAluno = acertosAluno+1
            else:
                    errosAluno = errosAluno+1
            if( (acertosAluno == 0 and errosAluno == 10) or (acertosAluno == 1 and errosAluno == 9) or (acertosAluno == 2 and errosAluno == 8) or (acertosAluno == 3 and errosAluno == 7) or (acertosAluno == 4 and errosAluno == 6)):
                nivelDoAluno = "Insuficiente"
            elif(acertosAluno == 5 and errosAluno == 5):
                nivelDoAluno = "Básico"
            elif((acertosAluno == 6 and errosAluno == 4) or (acertosAluno == 7 and errosAluno == 3) or (acertosAluno == 8 and errosAluno == 2) ):
                nivelDoAluno = "Proficiente"
            elif((acertosAluno == 9 and errosAluno == 1) or (acertosAluno == 10 and errosAluno == 0)):
                nivelDoAluno = "Avançado"
            aluno = request.POST.get("aluno")
            alunoExiste = acertosErros.objects.filter(aluno=ra)
            if not alunoExiste:
                pk_aluno = Aluno.objects.get(pk=ra)
                resultadosAluno = acertosErros()

                resultadosAluno.aluno= pk_aluno
                resultadosAluno.acertos= acertosAluno
                resultadosAluno.erros = errosAluno
                resultadosAluno.nivelDoAluno = nivelDoAluno

                resultadosAluno.save()
                
            else:
                
                atualizarAcertos = acertosErros.objects.filter(aluno=ra).values_list("acertos",flat=True).first()
                atualizarAcertos +=acertosAluno
                atualizarErros = acertosErros.objects.filter(aluno=ra).values_list("erros",flat=True).first()
                atualizarErros +=errosAluno

                if( atualizarAcertos <=5 ):
                    nivelDoAluno = "Insuficiente"
                elif(atualizarAcertos == 5 ):
                    nivelDoAluno = "Básico"
                elif(atualizarAcertos > 5 and atualizarAcertos <= 8 ):
                    nivelDoAluno = "Proficiente"
                elif(atualizarAcertos > 8):
                    nivelDoAluno = "Avançado"
                atualizarAcertosErros = acertosErros.objects.filter(aluno=ra).update(acertos=atualizarAcertos,erros=atualizarErros,nivelDoAluno=nivelDoAluno)
            return redirect("../telaAluno/"+str(ra))

        return render(request, "formularioAluno.html", {"ra":ra,"questao1": questao1,"alternativaAquestao1":alternativaAquestao1, "alternativaBquestao1":alternativaBquestao1,"alternativaCquestao1":alternativaCquestao1,"alternativaDquestao1":alternativaDquestao1,"questao2":questao2,"alternativaAquestao2":alternativaAquestao2, "alternativaBquestao2":alternativaBquestao2,"alternativaCquestao2":alternativaCquestao2,"alternativaDquestao2":alternativaDquestao2,"questao3":questao3,"alternativaAquestao3":alternativaAquestao3, "alternativaBquestao3":alternativaBquestao3,"alternativaCquestao3":alternativaCquestao3,"alternativaDquestao3":alternativaDquestao3,"questao4":questao4,"alternativaAquestao4":alternativaAquestao4, "alternativaBquestao4":alternativaBquestao4,"alternativaCquestao4":alternativaCquestao4,"alternativaDquestao4":alternativaDquestao4,"questao5":questao5,"alternativaAquestao5":alternativaAquestao5, "alternativaBquestao5":alternativaBquestao5,"alternativaCquestao5":alternativaCquestao5,"alternativaDquestao5":alternativaDquestao5,"questao6":questao6,"alternativaAquestao6":alternativaAquestao6, "alternativaBquestao6":alternativaBquestao6,"alternativaCquestao6":alternativaCquestao6,"alternativaDquestao6":alternativaDquestao6,"questao7":questao7,"alternativaAquestao7":alternativaAquestao7, "alternativaBquestao7":alternativaBquestao7,"alternativaCquestao7":alternativaCquestao7,"alternativaDquestao7":alternativaDquestao7,"questao8":questao8,"alternativaAquestao8":alternativaAquestao8, "alternativaBquestao8":alternativaBquestao8,"alternativaCquestao8":alternativaCquestao8,"alternativaDquestao8":alternativaDquestao8,"questao9":questao9,"alternativaAquestao9":alternativaAquestao9, "alternativaBquestao9":alternativaBquestao9,"alternativaCquestao9":alternativaCquestao9,"alternativaDquestao9":alternativaDquestao9,"questao10":questao10,"alternativaAquestao10":alternativaAquestao10, "alternativaBquestao10":alternativaBquestao10,"alternativaCquestao10":alternativaCquestao10,"alternativaDquestao10":alternativaDquestao10})

'''def pagina_feedback(request):
    if 'Log out' in request.POST:
        return redirect("telaProfessor")
    return render(request, "graficosFeedback.html")'''
        



