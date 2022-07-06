from datetime import datetime
from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password, check_password
from website.forms import AlunoForm, ProfessorForm
from website.models import Aluno, Professor
from django.contrib import messages

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

def pagina_aluno(request):
    form = AlunoForm(request.POST)
    return render(request,"pagina_aluno.html")

def pagina_professor(request):
    form = ProfessorForm(request.POST)
    return render(request,"pagina_professor.html")
