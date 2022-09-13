from audioop import reverse
from django.urls import NoReverseMatch
import stat
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
from django.urls import reverse
import os
import subprocess as sp
from stat import S_IREAD

def cadastro(request):
    professor = Professor()
    if request.method == 'POST':
        try: 
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
                professor = Professor()
                if (professor.esta_ativo == False):
                    al_nome = request.POST.get("al_nome")
                    senha = request.POST.get("al_senha")            
                    confir_senha = request.POST.get("confir_senha")
                    if senha != confir_senha:
                        messages.error(request,"As senhas inseridas são diferentes")
                        return redirect("/Teladecadastroaluno")
                    else:
                        al_senha = make_password(senha)
                        autenticar_usuario = User(username=al_nome, password=al_senha)
                        autenticar_usuario.save()       
                        user = Aluno.objects.create(al_nome=al_nome, al_email=al_email,al_nascimento=al_nascimento,al_senha=al_senha)
                        user.save()  
                else:                   
                    al_nome = request.POST.get("al_nome")
                    materia = request.POST.get("pf_materia")
                    senha = request.POST.get("al_senha")            
                    confir_senha = request.POST.get("confir_senha")
                    if senha != confir_senha:
                        messages.error(request,"As senhas inseridas são diferentes")
                        return redirect("/CadastroProfessor")
                    else:              
                            al_senha = make_password(senha)
                            autenticar_usuario = User(username=al_nome, password=al_senha)
                            autenticar_usuario.save()       
                            user = Professor.objects.create(pf_email=al_email,pf_nascimento=al_nascimento,materia=materia)
                            user.save()
                messages.success(request,"Conta criada com sucesso")           
                return redirect("/login")           
            except (ValueError,ValidationError):
                messages.error(request, "Data de nascimento inválida")  
            except AttributeError:
                messages.error(request,"Preencha os campos com dados válidos")
            except (Aluno.MultipleObjectsReturned,Professor.MultipleObjectsReturned,IntegrityError):  
                messages.error(request,"Preencha todos os campos")
    if (professor.esta_ativo== False):        
        return render(request, 'Teladecadastroaluno.html')
    else:
        return render(request, 'CadastroProfessor.html')

def login_user(request):        
            professor = Professor()
            if 'login' in request.POST:
                try:
                    al_nome = request.POST.get("al_nome")
                    al_senha = request.POST.get("al_senha")
                    professor = Professor()
                    if (professor.esta_ativo == False):
                        usuario = Aluno.objects.get(al_nome=al_nome)
                    else:
                        usuario = User.objects.get(username=al_nome)
                    if not al_nome or not al_senha:
                        messages.error(request, "Preencha todos os campos")
                        return redirect('login')
                    if usuario:
                        professor = Professor()                       
                        if (professor.esta_ativo == False):
                            checar_senha=check_password(al_senha, usuario.al_senha)
                        else:
                            usuario = User.objects.get(username=al_nome)
                            checar_senha=check_password(al_senha, usuario.password)
                        if checar_senha:
                            if (professor.esta_ativo == False):        
                                autenticar_usuario = authenticate(username=al_nome, password=al_senha, backend= 'django.contrib.auth.backends.AllowAllUsersModelBackend')                    
                                login(request, autenticar_usuario)
                                return redirect('telaAluno/'+str(usuario.ra)) 
                            else: 
                                prof = Professor.objects.get(Usuario_id = usuario.id)          
                                autenticar_usuario = authenticate(username=al_nome, password=al_senha, backend= 'django.contrib.auth.backends.AllowAllUsersModelBackend')            
                                login(request, autenticar_usuario)
                                return redirect('telaProfessor/'+str(prof.idProfessor))                          
                except (Aluno.DoesNotExist, Professor.DoesNotExist,User.DoesNotExist):   
                    messages.error(request, "Nome de usuário ou/e senha inválido(s)")
                except (Aluno.MultipleObjectsReturned,Professor.DoesNotExist,User.MultipleObjectsReturned,Professor.MultipleObjectsReturned):
                    autenticar_usuario = User.objects.filter(username=al_nome).first()
                    if autenticar_usuario:
                        login(request, autenticar_usuario)
                        professor = Professor()
                        if (professor.esta_ativo == False):
                            return redirect('telaAluno/'+str(user.ra)) 
                        else:
                            login(request, autenticar_usuario)
                            user = Professor.objects.get(pf_nome=al_nome).first()
                            return redirect('telaProfessor/'+str(user.idProfessor))
            elif 'cadastro' in request.POST:
                if (professor.esta_ativo == False):
                    return redirect('Teladecadastroaluno')
                else:
                    return redirect('CadastroProfessor')  
            return render(request,"login.html")

def atividades(request, ra):
    material_aluno = EnviarArquivo.objects.filter(alu=ra)
    return render(request,'atividades.html',{'material_aluno':material_aluno})

def visualizar_arquivo(request,arquivo):
    try:
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
    except(FileNotFoundError,ValueError):
            messages.error(request,"Arquivo não encontrado")
            fk_alu = request.GET.get("alu",'') 
            return redirect('../atividades/'+str(fk_alu))
    

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
    
@login_required(login_url='/login')
def feedback(request):
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
            return redirect("/feedback")
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
            alunos_ra = request.POST.getlist('aluno_ra')
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

@login_required(login_url='/login')
def pagina_aluno(request):
    return render(request,"pagina_aluno.html")


def pagina_professor(request,idProfessor):
    professor = idProfessor

    if 'turmas' in request.POST:
        return redirect("/turmas/"+str(idProfessor))
    elif 'Log out' in request.POST:
        sair(request)
        return redirect("login")
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