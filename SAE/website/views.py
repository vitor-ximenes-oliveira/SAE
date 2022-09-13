from audioop import reverse
from multiprocessing.sharedctypes import Value
from operator import truediv
from urllib.request import Request
from django.urls import NoReverseMatch
import stat
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password, check_password
from website.models import RespostasFormulario
from website.models import Aluno, EnviarArquivo, Feedback, Professor, Turmas, Formulario
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
from django.urls import reverse
import os
import subprocess as sp
from stat import S_IREAD

def cadastro_professor(request):
    try:
        if request.method == 'POST':
            pf_email =  request.POST.get("al_email")
            checar_email = Professor.objects.get(Email = pf_email)
            if checar_email:
                messages.error(request, "Já existe um professor cadastrado com esse e-mail")
    except (Professor.DoesNotExist):
            pf_nome = request.POST.get("al_nome")
            pf_email = request.POST.get("al_email")
            pf_nascimento = request.POST.get("al_nascimento")
            materia = request.POST.get("pf_materia")
            try:
                senha = request.POST.get("al_senha")            
                confir_senha = request.POST.get("confir_senha")
                if senha != confir_senha:
                        messages.error(request,"As senhas inseridas são diferentes")
                        return redirect("/CadastroProfessor")
                else:                                       
                                pf_senha = make_password(senha)
                                autenticar_usuario = User(username=pf_nome, password=pf_senha)
                                autenticar_usuario.save()       
                                id_user = User.objects.get(username=pf_nome) 
                                user = Professor.objects.create(Usuario=id_user,Nome = pf_nome,Email=pf_email,Nascimento=pf_nascimento,Materia=materia)
                                user.isProf = True
                                sim = Aluno.objects.update(isProf=0)   
                                user.save()
                                return redirect('login')
            except (ValueError,ValidationError):
                messages.error(request, "Data de nascimento inválida")  
            except AttributeError:
                messages.error(request,"Preencha os campos com dados válidos")
            except (Professor.MultipleObjectsReturned):  
                messages.error(request,"Preencha todos os campos")
            except (IntegrityError):
                messages.error(request,"Já existe um usuário cadastrado com esse nome") 
    return render(request,'CadastroProfessor.html')

def cadastro_aluno(request):
    if request.method == 'POST':
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
                            user.isProf = True
                            user.save()
                            sim = Professor.objects.update(isProf=0)                  
                            messages.success(request,"Conta criada com sucesso")  
                            
                            
                            return redirect('login')
                    except (ValueError,ValidationError):
                        messages.error(request, "Data de nascimento inválida")  
                    except AttributeError:
                        messages.error(request,"Preencha os campos com dados válidos")
                    except (Aluno.MultipleObjectsReturned):  
                        messages.error(request,"Preencha todos os campos") 
                    except (IntegrityError):
                        messages.error(request,"Já existe um usuário cadastrado com esse nome")
    return render(request,'Teladecadastroaluno.html')

def login_user(request):
            
            professor = Professor()
            if 'login' in request.POST:        
                try:
                    al_nome = request.POST.get("nome")
                    al_senha = request.POST.get("senha")
                    professor = Professor()
                    teste = Professor.objects.filter(isProf=1).last()
                    if (teste is None):
                        usuario = Aluno.objects.get(al_nome=al_nome)
                    else:
                        usuario = User.objects.get(username=al_nome)
                    if not al_nome or not al_senha:
                        messages.error(request, "Preencha todos os campos")
                        return redirect('login')
                    if usuario:
                        professor = Professor()                       
                        teste = Professor.objects.filter(isProf=1).last()
                        if (teste is None):
                            checar_senha=check_password(al_senha, usuario.al_senha)
                        else:
                            usuario = User.objects.get(username=al_nome)
                            checar_senha=check_password(al_senha, usuario.password)
                        if checar_senha:
                            teste = Professor.objects.filter(isProf=1).last()
                            if (teste is None):       
                                autenticar_usuario = authenticate(username=al_nome, password=al_senha, backend= 'django.contrib.auth.backends.AllowAllUsersModelBackend')                    
                                login(request, autenticar_usuario)
                                return redirect('telaAluno/'+str(usuario.ra)) 
                            else: 
                                prof = Professor.objects.get(Usuario_id = usuario.id)          
                                autenticar_usuario = authenticate(username=al_nome, password=al_senha, backend= 'django.contrib.auth.backends.AllowAllUsersModelBackend')            
                                login(request, autenticar_usuario)
                                mudar_campo_nome = Professor.objects.filter(Usuario=usuario).update(Nome=al_nome)
                                return redirect('telaProfessor/'+str(prof.idProfessor))                          
                
                except (Aluno.DoesNotExist):
                    try:
                        usuario = User.objects.get(username=al_nome)
                        if not al_nome or not al_senha:
                            messages.error(request, "Preencha todos os campos")
                            return redirect('login')
                        if usuario:
                            professor = Professor()                       
                            teste = Professor.objects.filter(isProf=1).last()
                            usuario = User.objects.get(username=al_nome)
                            checar_senha=check_password(al_senha, usuario.password)
                            if checar_senha:
                                    prof = Professor.objects.get(Usuario_id = usuario.id)          
                                    autenticar_usuario = authenticate(username=al_nome, password=al_senha, backend= 'django.contrib.auth.backends.AllowAllUsersModelBackend')            
                                    login(request, autenticar_usuario)
                                    mudar_campo_nome = Professor.objects.filter(Usuario=usuario).update(Nome=al_nome)
                                    return redirect('telaProfessor/'+str(prof.idProfessor))   
                    except(Professor.DoesNotExist,User.DoesNotExist):   
                        messages.error(request, "Nome de usuário ou/e senha inválido(s)")
                                        
                except (Aluno.MultipleObjectsReturned,User.MultipleObjectsReturned,Professor.MultipleObjectsReturned):
                    autenticar_usuario = User.objects.filter(username=al_nome).first()
                    if autenticar_usuario:
                        login(request, autenticar_usuario)
                        professor = Professor()
                        teste = Professor.objects.filter(isProf=1).last()
                        if (teste is None):
                            return redirect('telaAluno/'+str(user.ra)) 
                        else:
                            login(request, autenticar_usuario)
                            user = Professor.objects.get(Nome=al_nome).first()
                            return redirect('telaProfessor/'+str(user.idProfessor))
                except(Professor.DoesNotExist,User.DoesNotExist):   
                        messages.error(request, "Nome de usuário ou/e senha inválido(s)")
            elif 'cadastro' in request.POST:
                teste = Professor.objects.filter(isProf=1).last()
                alu= Aluno.objects.filter(isProf=1).last()
                print("ALU: ",alu)
                if professor.esta_ativo == True:
                        return redirect('/Teladecadastroaluno')
                else:
                        return redirect('/CadastroProfessor')
            return render(request,"Login.html")

def atividades(request, ra):
    material_aluno = EnviarArquivo.objects.filter(alu=ra)
    return render(request,'atividades.html',{'material_aluno':material_aluno,'ra':ra})

def visualizar_arquivo(request,arquivo):
    extensoes = [".pdf", ".txt", ".png", ".jpg", ".gif", ".bmp",".mp3",".mp4",'.JPG']
    if arquivo.endswith(tuple(extensoes)):
        diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)
        arquivo = open(diretorio_arquivo, 'rb') 
        abrir_Arquivo = FileResponse(arquivo)
        return abrir_Arquivo
    elif arquivo.endswith('.xlsx'):
        diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)
        os.system(diretorio_arquivo)    
        os.chmod(diretorio_arquivo,stat.S_IRWXO)                   
        fk_alu = request.GET.get("alu",'')      
        return redirect('../atividades/'+str(fk_alu))
    elif arquivo.endswith('.docx'): 
        diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)        
        sp.Popen(["C:\Program Files\Windows NT\Accessories\WordPad.exe", diretorio_arquivo])
        os.chmod(diretorio_arquivo,stat.S_IWUSR and stat.S_IRUSR and stat.S_IRUSR)  
        fk_alu = request.GET.get("alu",'')      
        return redirect('../atividades/'+str(fk_alu))
    elif arquivo.endswith('.pptx'):
        diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)
        os.system(diretorio_arquivo)    
        os.chmod(diretorio_arquivo,stat.S_IRWXO) 
        fk_alu = request.GET.get("alu",'')      
        return redirect('../atividades/'+str(fk_alu))
    else:
        diretorio_arquivo = os.path.join(settings.MEDIA_ROOT, arquivo)
        os.system(diretorio_arquivo)    
        os.chmod(diretorio_arquivo,S_IREAD)  
        fk_alu = request.GET.get("alu",'')      
        return redirect('../atividades/'+str(fk_alu))
    #except(FileNotFoundError,ValueError):
    #        messages.error(request,"Arquivo não encontrado")
    #        fk_alu = request.GET.get("alu",'') 
    #        return redirect('../atividades/'+str(fk_alu))
    
def baixar_arquivo(request, arquivo):
    try:
        if arquivo != '':
            diretorio_arquivo = (os.path.join(settings.MEDIA_ROOT, arquivo))
            diretorio = open(diretorio_arquivo,'rb')
            download_arquivo = HttpResponse(diretorio ,content_type="aplicacao/arquivo")
            download_arquivo ['Content-Disposition'] = "attachment; nome_arquivo=" + arquivo
            return download_arquivo
    except(FileNotFoundError,ValueError):
            messages.error(request,"Arquivo não encontrado")
            fk_alu = request.GET.get("alu",'')      
            return redirect('../atividades/'+str(fk_alu))
    
#@login_required(login_url='/login')
def feedback(request,ra):
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
            feedback = Feedback.objects.create(pergunta1=pergunta1,justificativa1=justificativa1,pergunta2=pergunta2,justificativa2=justificativa2,pergunta3=pergunta3,justificativa3=justificativa3,pergunta4=pergunta4,justificativa4=justificativa4,pergunta5=pergunta5,justificativa5=justificativa5,pergunta6=pergunta6,justificativa6=justificativa6,pergunta7=pergunta7,justificativa7=justificativa7,pergunta8=pergunta8,justificativa8=justificativa8,pergunta9=pergunta9,justificativa9=justificativa9)
            feedback.save() 
            messages.success(request,"Feedback enviado com sucesso")           
            return redirect("../telaAluno/"+str(ra))
    return render(request, 'feedback.html')

def sair(request):
        logout(request)
        messages.success(request,"Você saiu do seu perfil")
        return HttpResponseRedirect("/")

def turmas(request,idProfessor):
        if request.method == 'POST':
            classe = request.POST.get('classe')
            classe_aux = request.POST.get('classe')
            alunos = Aluno.objects.raw("select a.ra, a.al_nome, a.al_email, al_nascimento from aluno a join turmas t on a.ra = t.alu_id join Professor p on t.prof_id = idProfessor where t.classe =%s and t.prof_id = %s group by a.al_nome order by a.ra",(str(classe),str(idProfessor)))
            turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe",[idProfessor])#Mudei
        else:
            alunos = ""
            classe_aux = ""
            turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe",[idProfessor])#Mudei     
        return render(request, 'turmas.html', {'turmas': turmas,'alunos':alunos,'classe_aux':classe_aux})

def enviar_arquivo(request,idProfessor):
    if 'atualizar' in request.POST:
        classe = request.POST.get('classe')
        classe_aux = request.POST.get('classe')
        alunos = Aluno.objects.raw("select a.ra, a.al_nome from aluno a join turmas t on a.ra = t.alu_id join Professor p on t.prof_id = idProfessor where t.classe =%s and t.prof_id = %s group by a.al_nome",(str(classe),str(idProfessor)))
        turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe",str(idProfessor))        
    elif 'enviar' in request.POST:
        try:
            classe = request.POST.get('classe')
            classe_aux = request.POST.get('classe')            
            turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe",str(idProfessor))   
            alunos = Aluno.objects.raw("select a.ra, a.al_nome from aluno a join turmas t on a.ra = t.alu_id join Professor p on t.prof_id = idProfessor where t.classe =%s and t.prof_id = %s group by a.al_nome",(str(classe),str(idProfessor)))
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
        classe_aux = ""
        turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe",str(idProfessor))         
    return render(request, 'enviar_arquivo.html', {'turmas': turmas,'alunos':alunos,'classe_aux':classe_aux})


def telaAluno(request,ra):
    if 'feedback' in request.POST:
        return redirect("/feedback/"+str(ra))
    elif 'Log out' in request.POST:
        sair(request)
        return redirect("login")
    elif 'atividades' in request.POST:
        return redirect('atividades',ra)
    elif 'formularioAluno' in request.POST:
        return redirect('/formularioAluno/'+str(ra))
    return render(request,"telaAluno.html")


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
        return redirect("inserir_classe")
    elif 'enviar_arquivo' in request.POST:
        return redirect("/enviar_arquivo/"+str(idProfessor))

    return render(request,"telaProfessor.html")

def inserir_classe(request):
    if 'enviar' in request.POST:
        try:
            alunos = Aluno.objects.all()
            ano_letivo = request.POST.get("ano_letivo")
            classe = request.POST.get("classe")
            professores = Professor.objects.all()
            idProfessor = request.POST.get("professor")
            profi = Turmas.objects.filter(prof=idProfessor).values_list('prof_id',flat=True).first()
            nova_turma = Turmas.objects.get(ano_letivo=ano_letivo,classe=classe,prof=profi)
            if idProfessor is None:
                messages.error(request,"Selecione um professor")
                return redirect('inserir_classe')
        except Turmas.MultipleObjectsReturned:         
                messages.error(request,"Já existe uma turma com essas informações")
                return redirect('/inserir_classe')
        except Turmas.DoesNotExist:
            if request.POST.get("classe") and request.POST.get("ano_letivo"):
                alunos_selecionados = request.POST.getlist('aluno_ra')
                if idProfessor is None or not alunos_selecionados:
                        messages.error(request,"Preencha todos os campos da opção que deseja executar")
                        return redirect("/inserir_classe")
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
                return redirect("/inserir_classe")  
        turmas = Turmas.objects.raw("SELECT * from turmas t join professor p on t.prof_id = p.idProfessor group by classe,prof_id")  
    elif 'classe_existente' in request.POST:
        alunos = Aluno.objects.all()
        professores = Professor.objects.all()
        turmas = Turmas.objects.raw("SELECT * from turmas t join professor p on t.prof_id = p.idProfessor group by classe,prof_id")  
        try:   
            if request.POST.get("idProfessor"):
                idProfessor = request.POST.get("idProfessor")   
                for prof_id in Professor.objects.values_list("idProfessor",flat=True):
                    if str(prof_id) == str(idProfessor):    
                        return redirect(reverse('editar_classe',args=[idProfessor]))  
                messages.error(request,"ID inválido")
            else:    
                    messages.error(request,"Insira o ID do professor")
        except ValueError:
                    messages.error(request,"Não existe um professor com esse ID")
                    return redirect("/inserir_classe")
        except NoReverseMatch:
            messages.error(request,"Insira um ID do professor que seja válido")
            return redirect("/inserir_classe")
    else:     
        professores = Professor.objects.all()
        alunos = Aluno.objects.all()
        turmas = Turmas.objects.raw("SELECT * from turmas t join professor p on t.prof_id = p.idProfessor group by classe,prof_id")  
    return render(request, "inserir_classe.html",{'alunos':alunos,'professores':professores,'turmas':turmas})

def editar_classe(request,idProfessor):              
        if 'editar' in request.POST:          
            classe = request.POST.get("classe")
            classe_aux = request.POST.get('classe')
            alunos = request.POST.getlist('aluno_ra')
            if not alunos:
                messages.error(request,"Selecione um aluno")
                return redirect('editar_classe',idProfessor)
            for aluno in alunos:                        
                    turmas = Turmas()
                    id_professor = Professor.objects.get(pk=idProfessor)
                    turmas.prof = id_professor
                    id_aluno = Aluno.objects.get(pk=aluno)                
                    turmas.alu = id_aluno
                    turmas.classe = classe
                    ano_letivo = Turmas.objects.filter(classe=classe).values_list('ano_letivo',flat=True).first()
                    turmas.ano_letivo = ano_letivo                    
                    turmas.save()
                    messages.success(request,"Turma atualizada com sucesso")
            alunos = Aluno.objects.raw("select a.ra,t.prof_id,classe,alu_id from aluno a left outer join turmas t on t.alu_id = a.ra where alu_id not in (select alu_id from turmas where classe = %s and prof_id=%s or prof_id<>NULL) group by alu_id",[classe,idProfessor])
            turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe",str(idProfessor))
        elif 'atualizar' in request.POST:
            classe = request.POST.get('classe')
            classe_aux = request.POST.get('classe')
            ano_letivo = Turmas.objects.filter(classe=classe).values_list('ano_letivo',flat=True).first()
            turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe",[idProfessor])  
            alunos = Aluno.objects.raw("select a.ra,t.prof_id,classe,alu_id from aluno a left outer join turmas t on t.alu_id = a.ra where alu_id not in (select alu_id from turmas where classe = %s and prof_id=%s or prof_id<>NULL) group by alu_id",[classe,idProfessor])
        else:
            alunos = ""
            classe_aux = ""
            turmas = Turmas.objects.raw("SELECT idTurma, ano_letivo, classe, alu_id,prof_id FROM turmas where prof_id=%s GROUP BY classe",[idProfessor])
        return render(request, "editar_classe.html",{'alunos':alunos,'turmas':turmas,'classe_aux':classe_aux})

def graficosFeedback(request,idProfessor):
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

def criarFormulario(request,idProfessor):
    if request.method == 'POST':
            print("BATATA")
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
            formulario.save() 
            messages.success(request,"Formulario criado com sucesso")           
            return redirect("gabaritoFormulario",idProfessor)
      
    return render(request, 'criarFormulario.html')

def gabaritoFormulario(request,idProfessor):
        questao1 = Formulario.objects.values_list("questao1",flat=True).first()
        alternativaAquestao1 = Formulario.objects.values_list("alternativaAquestao1",flat=True).first()
        alternativaBquestao1 = Formulario.objects.values_list("alternativaBquestao1",flat=True).first()
        alternativaCquestao1 = Formulario.objects.values_list("alternativaCquestao1",flat=True).first()
        alternativaDquestao1 = Formulario.objects.values_list("alternativaDquestao1",flat=True).first()
        questao2 = Formulario.objects.values_list("questao2",flat=True).first()
        alternativaAquestao2 = Formulario.objects.values_list("alternativaAquestao2",flat=True).first()
        alternativaBquestao2 = Formulario.objects.values_list("alternativaBquestao2",flat=True).first()
        alternativaCquestao2 = Formulario.objects.values_list("alternativaCquestao2",flat=True).first()
        alternativaDquestao2 = Formulario.objects.values_list("alternativaDquestao2",flat=True).first()
        questao3 = Formulario.objects.values_list("questao3",flat=True).first()
        alternativaAquestao3 = Formulario.objects.values_list("alternativaAquestao3",flat=True).first()
        alternativaBquestao3 = Formulario.objects.values_list("alternativaBquestao3",flat=True).first()
        alternativaCquestao3 = Formulario.objects.values_list("alternativaCquestao3",flat=True).first()
        alternativaDquestao3 = Formulario.objects.values_list("alternativaDquestao3",flat=True).first()
        questao4 = Formulario.objects.values_list("questao4",flat=True).first()
        alternativaAquestao4 = Formulario.objects.values_list("alternativaAquestao4",flat=True).first()
        alternativaBquestao4 = Formulario.objects.values_list("alternativaBquestao4",flat=True).first()
        alternativaCquestao4 = Formulario.objects.values_list("alternativaCquestao4",flat=True).first()
        alternativaDquestao4 = Formulario.objects.values_list("alternativaDquestao4",flat=True).first()
        questao5 = Formulario.objects.values_list("questao5",flat=True).first()
        alternativaAquestao5 = Formulario.objects.values_list("alternativaAquestao5",flat=True).first()
        alternativaBquestao5 = Formulario.objects.values_list("alternativaBquestao5",flat=True).first()
        alternativaCquestao5 = Formulario.objects.values_list("alternativaCquestao5",flat=True).first()
        alternativaDquestao5 = Formulario.objects.values_list("alternativaDquestao5",flat=True).first()
        questao6 = Formulario.objects.values_list("questao6",flat=True).first()
        alternativaAquestao6 = Formulario.objects.values_list("alternativaAquestao6",flat=True).first()
        alternativaBquestao6 = Formulario.objects.values_list("alternativaBquestao6",flat=True).first()
        alternativaCquestao6 = Formulario.objects.values_list("alternativaCquestao6",flat=True).first()
        alternativaDquestao6 = Formulario.objects.values_list("alternativaDquestao6",flat=True).first()
        questao7 = Formulario.objects.values_list("questao7",flat=True).first()
        alternativaAquestao7 = Formulario.objects.values_list("alternativaAquestao7",flat=True).first()
        alternativaBquestao7 = Formulario.objects.values_list("alternativaBquestao7",flat=True).first()
        alternativaCquestao7 = Formulario.objects.values_list("alternativaCquestao7",flat=True).first()
        alternativaDquestao7 = Formulario.objects.values_list("alternativaDquestao7",flat=True).first()
        questao8 = Formulario.objects.values_list("questao8",flat=True).first()
        alternativaAquestao8 = Formulario.objects.values_list("alternativaAquestao8",flat=True).first()
        alternativaBquestao8 = Formulario.objects.values_list("alternativaBquestao8",flat=True).first()
        alternativaCquestao8 = Formulario.objects.values_list("alternativaCquestao8",flat=True).first()
        alternativaDquestao8 = Formulario.objects.values_list("alternativaDquestao8",flat=True).first()
        questao9 = Formulario.objects.values_list("questao9",flat=True).first()
        alternativaAquestao9 = Formulario.objects.values_list("alternativaAquestao9",flat=True).first()
        alternativaBquestao9 = Formulario.objects.values_list("alternativaBquestao9",flat=True).first()
        alternativaCquestao9 = Formulario.objects.values_list("alternativaCquestao9",flat=True).first()
        alternativaDquestao9 = Formulario.objects.values_list("alternativaDquestao9",flat=True).first()
        questao10 = Formulario.objects.values_list("questao10",flat=True).first()
        alternativaAquestao10 = Formulario.objects.values_list("alternativaAquestao10",flat=True).first()
        alternativaBquestao10 = Formulario.objects.values_list("alternativaBquestao10",flat=True).first()
        alternativaCquestao10 = Formulario.objects.values_list("alternativaCquestao10",flat=True).first()
        alternativaDquestao10 = Formulario.objects.values_list("alternativaDquestao10",flat=True).first()
        
        
        if 'gabarito' in request.POST:
            respostaQuestao1 = request.POST.get("btn-radio")
            print("TESTE: ",respostaQuestao1)
            respostaQuestao2 = request.POST.get("btn-radio2")
            respostaQuestao3 = request.POST.get("btn-radio3")
            respostaQuestao4 = request.POST.get("btn-radio4")
            respostaQuestao5 = request.POST.get("btn-radio5")
            respostaQuestao6 = request.POST.get("btn-radio6")
            respostaQuestao7 = request.POST.get("btn-radio7")
            respostaQuestao8 = request.POST.get("btn-radio8")
            respostaQuestao9 = request.POST.get("btn-radio9")
            respostaQuestao10 = request.POST.get("btn-radio10")
            print("sim")
            gabarito = RespostasFormulario.objects.create(respostaQuestao1=respostaQuestao1,respostaQuestao2=respostaQuestao2,respostaQuestao3=respostaQuestao3,respostaQuestao4=respostaQuestao4,respostaQuestao5=respostaQuestao5,respostaQuestao6=respostaQuestao6,respostaQuestao7=respostaQuestao7,respostaQuestao8=respostaQuestao8,respostaQuestao9=respostaQuestao9,respostaQuestao10=respostaQuestao10)
            gabarito.save() 
            print("teste2")
            messages.success(request,"Gabarito enviado com sucesso")  
            return redirect("../telaProfessor/"+str(idProfessor))
    
        
        return render(request, "gabaritoFormulario.html", {"questao1": questao1,"alternativaAquestao1":alternativaAquestao1, "alternativaBquestao1":alternativaBquestao1,"alternativaCquestao1":alternativaCquestao1,"alternativaDquestao1":alternativaDquestao1,"questao2":questao2,"alternativaAquestao2":alternativaAquestao2, "alternativaBquestao2":alternativaBquestao2,"alternativaCquestao2":alternativaCquestao2,"alternativaDquestao2":alternativaDquestao2,"questao3":questao3,"alternativaAquestao3":alternativaAquestao3, "alternativaBquestao3":alternativaBquestao3,"alternativaCquestao3":alternativaCquestao3,"alternativaDquestao3":alternativaDquestao3,"questao4":questao4,"alternativaAquestao4":alternativaAquestao4, "alternativaBquestao4":alternativaBquestao4,"alternativaCquestao4":alternativaCquestao4,"alternativaDquestao4":alternativaDquestao4,"questao5":questao5,"alternativaAquestao5":alternativaAquestao5, "alternativaBquestao5":alternativaBquestao5,"alternativaCquestao5":alternativaCquestao5,"alternativaDquestao5":alternativaDquestao5,"questao6":questao6,"alternativaAquestao6":alternativaAquestao6, "alternativaBquestao6":alternativaBquestao6,"alternativaCquestao6":alternativaCquestao6,"alternativaDquestao6":alternativaDquestao6,"questao7":questao7,"alternativaAquestao7":alternativaAquestao7, "alternativaBquestao7":alternativaBquestao7,"alternativaCquestao7":alternativaCquestao7,"alternativaDquestao7":alternativaDquestao7,"questao8":questao8,"alternativaAquestao8":alternativaAquestao8, "alternativaBquestao8":alternativaBquestao8,"alternativaCquestao8":alternativaCquestao8,"alternativaDquestao8":alternativaDquestao8,"questao9":questao9,"alternativaAquestao9":alternativaAquestao9, "alternativaBquestao9":alternativaBquestao9,"alternativaCquestao9":alternativaCquestao9,"alternativaDquestao9":alternativaDquestao9,"questao10":questao10,"alternativaAquestao10":alternativaAquestao10, "alternativaBquestao10":alternativaBquestao10,"alternativaCquestao10":alternativaCquestao10,"alternativaDquestao10":alternativaDquestao10})
    
def graficoAluno(request,ra):
    if 'graficoAluno' in request.POST:
        acertos = 0
        erros = 0

        nivelDoAluno = ""

        questao1 = RespostasFormulario.objects.values_list("respostaQuestao1",flat=True).first()
        questao2 = RespostasFormulario.objects.values_list("respostaQuestao2",flat=True).first()
        questao3 = RespostasFormulario.objects.values_list("respostaQuestao3",flat=True).first()
        questao4 = RespostasFormulario.objects.values_list("respostaQuestao4",flat=True).first()
        questao5 = RespostasFormulario.objects.values_list("respostaQuestao5",flat=True).first()
        questao6 = RespostasFormulario.objects.values_list("respostaQuestao6",flat=True).first()
        questao7 = RespostasFormulario.objects.values_list("respostaQuestao7",flat=True).first()
        questao8 = RespostasFormulario.objects.values_list("respostaQuestao8",flat=True).first()
        questao9 = RespostasFormulario.objects.values_list("respostaQuestao9",flat=True).first()
        questao10 = RespostasFormulario.objects.values_list("respostaQuestao10",flat=True).first()
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

        if(questao1 == resposta1):
            acertos+=1
        else:
            erros+=1

        if(questao2 == resposta2):
            acertos+=1
        else:
            erros+=1

        if(questao3 == resposta3):
            acertos+=1
        else:
            erros+=1

        if(questao4 == resposta4):
            acertos+=1
        else:
            erros+=1

        if(questao5 == resposta5):
            acertos+=1
        else:
            erros+=1

        if(questao6 == resposta6):
            acertos+=1
        else:
            erros+=1

        if(questao7 == resposta7):
            acertos+=1
        else:
            erros+=1

        if(questao8 == resposta8):
            acertos+=1
        else:
            erros+=1

        if(questao9 == resposta9):
            acertos+=1
        else:
            erros+=1

        if(questao10 == resposta10):
            acertos+=1
        else:
            erros+=1

        if( acertos <=5 ):
            nivelDoAluno = "Insuficiente"
        elif(acertos == 5 ):
            nivelDoAluno = "Básico"
        elif(acertos > 5 and acertos <= 8 ):
            nivelDoAluno = "Proficiente"
        elif(acertos > 8):
            nivelDoAluno = "Avançado"

        #return redirect(request, "/telaAluno/"+str(ra) {"acertos":acertos, "erros": erros, "nivelDoAluno": nivelDoAluno})
    return render(request, "formularioAluno.html")

def formularioAluno(request,ra):
    questao1 = Formulario.objects.values_list("questao1",flat=True).first()
    alternativaAquestao1 = Formulario.objects.values_list("alternativaAquestao1",flat=True).first()
    alternativaBquestao1 = Formulario.objects.values_list("alternativaBquestao1",flat=True).first()
    alternativaCquestao1 = Formulario.objects.values_list("alternativaCquestao1",flat=True).first()
    alternativaDquestao1 = Formulario.objects.values_list("alternativaDquestao1",flat=True).first()
    questao2 = Formulario.objects.values_list("questao2",flat=True).first()
    alternativaAquestao2 = Formulario.objects.values_list("alternativaAquestao2",flat=True).first()
    alternativaBquestao2 = Formulario.objects.values_list("alternativaBquestao2",flat=True).first()
    alternativaCquestao2 = Formulario.objects.values_list("alternativaCquestao2",flat=True).first()
    alternativaDquestao2 = Formulario.objects.values_list("alternativaDquestao2",flat=True).first()
    questao3 = Formulario.objects.values_list("questao3",flat=True).first()
    alternativaAquestao3 = Formulario.objects.values_list("alternativaAquestao3",flat=True).first()
    alternativaBquestao3 = Formulario.objects.values_list("alternativaBquestao3",flat=True).first()
    alternativaCquestao3 = Formulario.objects.values_list("alternativaCquestao3",flat=True).first()
    alternativaDquestao3 = Formulario.objects.values_list("alternativaDquestao3",flat=True).first()
    questao4 = Formulario.objects.values_list("questao4",flat=True).first()
    alternativaAquestao4 = Formulario.objects.values_list("alternativaAquestao4",flat=True).first()
    alternativaBquestao4 = Formulario.objects.values_list("alternativaBquestao4",flat=True).first()
    alternativaCquestao4 = Formulario.objects.values_list("alternativaCquestao4",flat=True).first()
    alternativaDquestao4 = Formulario.objects.values_list("alternativaDquestao4",flat=True).first()
    questao5 = Formulario.objects.values_list("questao5",flat=True).first()
    alternativaAquestao5 = Formulario.objects.values_list("alternativaAquestao5",flat=True).first()
    alternativaBquestao5 = Formulario.objects.values_list("alternativaBquestao5",flat=True).first()
    alternativaCquestao5 = Formulario.objects.values_list("alternativaCquestao5",flat=True).first()
    alternativaDquestao5 = Formulario.objects.values_list("alternativaDquestao5",flat=True).first()
    questao6 = Formulario.objects.values_list("questao6",flat=True).first()
    alternativaAquestao6 = Formulario.objects.values_list("alternativaAquestao6",flat=True).first()
    alternativaBquestao6 = Formulario.objects.values_list("alternativaBquestao6",flat=True).first()
    alternativaCquestao6 = Formulario.objects.values_list("alternativaCquestao6",flat=True).first()
    alternativaDquestao6 = Formulario.objects.values_list("alternativaDquestao6",flat=True).first()
    questao7 = Formulario.objects.values_list("questao7",flat=True).first()
    alternativaAquestao7 = Formulario.objects.values_list("alternativaAquestao7",flat=True).first()
    alternativaBquestao7 = Formulario.objects.values_list("alternativaBquestao7",flat=True).first()
    alternativaCquestao7 = Formulario.objects.values_list("alternativaCquestao7",flat=True).first()
    alternativaDquestao7 = Formulario.objects.values_list("alternativaDquestao7",flat=True).first()
    questao8 = Formulario.objects.values_list("questao8",flat=True).first()
    alternativaAquestao8 = Formulario.objects.values_list("alternativaAquestao8",flat=True).first()
    alternativaBquestao8 = Formulario.objects.values_list("alternativaBquestao8",flat=True).first()
    alternativaCquestao8 = Formulario.objects.values_list("alternativaCquestao8",flat=True).first()
    alternativaDquestao8 = Formulario.objects.values_list("alternativaDquestao8",flat=True).first()
    questao9 = Formulario.objects.values_list("questao9",flat=True).first()
    alternativaAquestao9 = Formulario.objects.values_list("alternativaAquestao9",flat=True).first()
    alternativaBquestao9 = Formulario.objects.values_list("alternativaBquestao9",flat=True).first()
    alternativaCquestao9 = Formulario.objects.values_list("alternativaCquestao9",flat=True).first()
    alternativaDquestao9 = Formulario.objects.values_list("alternativaDquestao9",flat=True).first()
    questao10 = Formulario.objects.values_list("questao10",flat=True).first()
    alternativaAquestao10 = Formulario.objects.values_list("alternativaAquestao10",flat=True).first()
    alternativaBquestao10 = Formulario.objects.values_list("alternativaBquestao10",flat=True).first()
    alternativaCquestao10 = Formulario.objects.values_list("alternativaCquestao10",flat=True).first()
    alternativaDquestao10 = Formulario.objects.values_list("alternativaDquestao10",flat=True).first()
    if request.method == 'POST':


        return redirect("../telaAluno/"+str(ra))
    return render(request, "formularioAluno.html", {"questao1": questao1,"alternativaAquestao1":alternativaAquestao1, "alternativaBquestao1":alternativaBquestao1,"alternativaCquestao1":alternativaCquestao1,"alternativaDquestao1":alternativaDquestao1,"questao2":questao2,"alternativaAquestao2":alternativaAquestao2, "alternativaBquestao2":alternativaBquestao2,"alternativaCquestao2":alternativaCquestao2,"alternativaDquestao2":alternativaDquestao2,"questao3":questao3,"alternativaAquestao3":alternativaAquestao3, "alternativaBquestao3":alternativaBquestao3,"alternativaCquestao3":alternativaCquestao3,"alternativaDquestao3":alternativaDquestao3,"questao4":questao4,"alternativaAquestao4":alternativaAquestao4, "alternativaBquestao4":alternativaBquestao4,"alternativaCquestao4":alternativaCquestao4,"alternativaDquestao4":alternativaDquestao4,"questao5":questao5,"alternativaAquestao5":alternativaAquestao5, "alternativaBquestao5":alternativaBquestao5,"alternativaCquestao5":alternativaCquestao5,"alternativaDquestao5":alternativaDquestao5,"questao6":questao6,"alternativaAquestao6":alternativaAquestao6, "alternativaBquestao6":alternativaBquestao6,"alternativaCquestao6":alternativaCquestao6,"alternativaDquestao6":alternativaDquestao6,"questao7":questao7,"alternativaAquestao7":alternativaAquestao7, "alternativaBquestao7":alternativaBquestao7,"alternativaCquestao7":alternativaCquestao7,"alternativaDquestao7":alternativaDquestao7,"questao8":questao8,"alternativaAquestao8":alternativaAquestao8, "alternativaBquestao8":alternativaBquestao8,"alternativaCquestao8":alternativaCquestao8,"alternativaDquestao8":alternativaDquestao8,"questao9":questao9,"alternativaAquestao9":alternativaAquestao9, "alternativaBquestao9":alternativaBquestao9,"alternativaCquestao9":alternativaCquestao9,"alternativaDquestao9":alternativaDquestao9,"questao10":questao10,"alternativaAquestao10":alternativaAquestao10, "alternativaBquestao10":alternativaBquestao10,"alternativaCquestao10":alternativaCquestao10,"alternativaDquestao10":alternativaDquestao10})


def pagina_feedback(request):
    if 'Log out' in request.POST:
        return redirect("telaProfessor")
    return render(request, "graficosFeedback.html")
        



