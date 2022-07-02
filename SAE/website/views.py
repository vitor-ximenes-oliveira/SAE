from django.shortcuts import redirect, render
from django.contrib.auth.hashers import make_password, check_password
from website.forms import AlunoForm
from website.models import Aluno
from django.contrib import messages

def cadastro(request):
    form = AlunoForm(request.POST)
    if request.method == 'POST':
        try:   
            email =  request.POST.get("email")
            checar_email = Aluno.objects.get(email = email)
            if checar_email:
                messages.info(request, "Já existe um usuário cadastrado com esse e-mail")                   
        except Aluno.DoesNotExist:
            nome = request.POST.get("nome")
            email =  request.POST.get("email")
            senha = make_password(request.POST.get("senha"))                
            user = Aluno.objects.create(nome=nome, email=email,senha=senha) 
            user.save() 
            messages.success(request,"Contra criada com sucesso")           
            return redirect("/login")  
    return render(request, 'cadastro.html', {'form': form})

def login_user(request):        
            if request.method == 'POST':
                try:
                    nome = request.POST.get("nome")
                    senha = request.POST.get("senha")
                    user =Aluno.objects.get(nome=nome)
                    if user:
                        checar_senha=check_password(senha, user.senha)
                        if checar_senha:
                            return redirect('/pagina')
                except Aluno.DoesNotExist:        
                    messages.info(request, "Nome/senha inválido(s)")
            return render(request,"login.html")

def pagina(request):
    form = AlunoForm(request.POST)
    return (request,"Página inicial")
