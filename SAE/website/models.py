from django.db import models
from django.contrib.auth.models import User,AbstractUser
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core import validators
from datetime import *
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import os

class Aluno(models.Model):
    ra = models.AutoField(primary_key = True)
    al_nome = models.CharField(max_length=100)
    al_email = models.EmailField()
    al_senha = models.CharField(max_length=100)
    al_nascimento = models.DateField()
    isProf = models.BooleanField(default=0) 
    @property
    def esta_ativo(self):
            return bool(self.isProf)   
    class Meta:
        db_table = "Aluno"

class Turmas(models.Model):
    idTurma = models.AutoField(primary_key=True)
    ano_letivo = models.CharField(max_length=10,blank = False)
    classe = models.CharField(max_length=10,blank = False)
    alu = models.ForeignKey('Aluno', on_delete = models.CASCADE,related_name='classes')
    prof = models.ForeignKey('Professor', blank= False,on_delete = models.CASCADE,related_name='classes')
    class Meta:
        db_table = 'turmas'
    def __str__(self):
        return "%s %s %s" %(self.idTurma,self.ano_letivo,self.classe)
        
        
OPCOES = [
        ('ruim','Ruim'),
        ('bom','Bom'),
        ('médio','Médio'),
        ('excelente','Excelente'),
]

class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    pergunta1 = models.CharField(max_length=10,choices=OPCOES, blank=False)
    justificativa1 = models.CharField(max_length=255,blank = True)
    pergunta2 = models.CharField(max_length=10, choices=OPCOES,blank = False)
    justificativa2 = models.CharField(max_length=255,blank = True)
    pergunta3 = models.CharField(max_length=10, choices=OPCOES,blank = False)
    justificativa3 = models.CharField(max_length=255,blank = True)
    pergunta4 = models.CharField(max_length=10, choices=OPCOES,blank = False)
    justificativa4 = models.CharField(max_length=255,blank = True)
    pergunta5 = models.CharField(max_length=10, choices=OPCOES,blank = False)
    justificativa5 = models.CharField(max_length=255,blank = True)
    pergunta6 = models.CharField(max_length=10, choices=OPCOES,blank = False)
    justificativa6 = models.CharField(max_length=255,blank = True)
    pergunta7 = models.CharField(max_length=10, choices=OPCOES,blank = False)
    justificativa7 = models.CharField(max_length=255,blank = True)
    pergunta8 = models.CharField(max_length=10, choices=OPCOES,blank = False)
    justificativa8 = models.CharField(max_length=255,blank = True)
    pergunta9 = models.CharField(max_length=10, choices=OPCOES,blank = False)
    justificativa9 = models.CharField(max_length=255,blank = True)
    class Meta:
        db_table = "feedback"


class EnviarArquivo(models.Model):
    idEnvio = models.AutoField(primary_key=True)
    arquivo = models.FileField(upload_to="", null=True, blank=True)
    alu = models.ForeignKey(Aluno,on_delete=models.CASCADE)
    def __str__(self):
        return "%s" %(self.arquivo)
    class Meta:
        db_table = "enviar_arquivo"

class Formulario(models.Model):
    id = models.AutoField(primary_key=True)
    questao1 = models.CharField(max_length=200,blank=True)
    alternativaAquestao1 = models.CharField(max_length=100,blank=True)
    alternativaBquestao1 = models.CharField(max_length=100,blank=True)
    alternativaCquestao1 = models.CharField(max_length=100,blank=True)
    alternativaDquestao1 = models.CharField(max_length=100,blank=True)
    questao2 = models.CharField(max_length=200,blank=True)
    alternativaAquestao2 = models.CharField(max_length=100,blank=True)
    alternativaBquestao2 = models.CharField(max_length=100,blank=True)
    alternativaCquestao2 = models.CharField(max_length=100,blank=True)
    alternativaDquestao2 = models.CharField(max_length=100,blank=True)
    questao3 = models.CharField(max_length=200,blank=True)
    alternativaAquestao3 = models.CharField(max_length=100,blank=True)
    alternativaBquestao3 = models.CharField(max_length=100,blank=True)
    alternativaCquestao3 = models.CharField(max_length=100,blank=True)
    alternativaDquestao3 = models.CharField(max_length=100,blank=True)
    questao4 = models.CharField(max_length=200,blank=True)
    alternativaAquestao4 = models.CharField(max_length=100,blank=True)
    alternativaBquestao4 = models.CharField(max_length=100,blank=True)
    alternativaCquestao4 = models.CharField(max_length=100,blank=True)
    alternativaDquestao4 = models.CharField(max_length=100,blank=True)
    questao5 = models.CharField(max_length=200,blank=True)
    alternativaAquestao5 = models.CharField(max_length=100,blank=True)
    alternativaBquestao5 = models.CharField(max_length=100,blank=True)
    alternativaCquestao5 = models.CharField(max_length=100,blank=True)
    alternativaDquestao5 = models.CharField(max_length=100,blank=True)
    questao6 = models.CharField(max_length=200,blank=True)
    alternativaAquestao6 = models.CharField(max_length=100,blank=True)
    alternativaBquestao6 = models.CharField(max_length=100,blank=True)
    alternativaCquestao6 = models.CharField(max_length=100,blank=True)
    alternativaDquestao6 = models.CharField(max_length=100,blank=True)
    questao7 = models.CharField(max_length=200,blank=True)
    alternativaAquestao7 = models.CharField(max_length=100,blank=True)
    alternativaBquestao7 = models.CharField(max_length=100,blank=True)
    alternativaCquestao7 = models.CharField(max_length=100,blank=True)
    alternativaDquestao7 = models.CharField(max_length=100,blank=True)
    questao8 = models.CharField(max_length=200,blank=True)
    alternativaAquestao8 = models.CharField(max_length=100,blank=True)
    alternativaBquestao8 = models.CharField(max_length=100,blank=True)
    alternativaCquestao8 = models.CharField(max_length=100,blank=True)
    alternativaDquestao8 = models.CharField(max_length=100,blank=True)
    questao9 = models.CharField(max_length=200,blank=True)
    alternativaAquestao9 = models.CharField(max_length=100,blank=True)
    alternativaBquestao9 = models.CharField(max_length=100,blank=True)
    alternativaCquestao9 = models.CharField(max_length=100,blank=True)
    alternativaDquestao9 = models.CharField(max_length=100,blank=True)
    questao10 = models.CharField(max_length=200,blank=True)
    alternativaAquestao10 = models.CharField(max_length=100,blank=True)
    alternativaBquestao10 = models.CharField(max_length=100,blank=True)
    alternativaCquestao10 = models.CharField(max_length=100,blank=True)
    alternativaDquestao10 = models.CharField(max_length=100,blank=True)
    respostaQuestao1 = models.CharField(max_length=100,blank=True)
    respostaQuestao2 = models.CharField(max_length=100,blank=True)
    respostaQuestao3 = models.CharField(max_length=100,blank=True)
    respostaQuestao4 = models.CharField(max_length=100,blank=True)
    respostaQuestao5 = models.CharField(max_length=100,blank=True)
    respostaQuestao6 = models.CharField(max_length=100,blank=True)
    respostaQuestao7 = models.CharField(max_length=100,blank=True)
    respostaQuestao8 = models.CharField(max_length=100,blank=True)
    respostaQuestao9 = models.CharField(max_length=100,blank=True)
    respostaQuestao10 = models.CharField(max_length=100,blank=True)

    class Meta:
        db_table = "formulario"

class RespostasFormulario(models.Model):
    id = models.AutoField(primary_key=True)
    #fk_aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE,blank=False)
    #nome_aluno = models.CharField(max_length=100,blank=True)
    respostaQuestao1 = models.CharField(max_length=100,blank=True)
    respostaQuestao2 = models.CharField(max_length=100,blank=True)
    respostaQuestao3 = models.CharField(max_length=100,blank=True)
    respostaQuestao4 = models.CharField(max_length=100,blank=True)
    respostaQuestao5 = models.CharField(max_length=100,blank=True)
    respostaQuestao6 = models.CharField(max_length=100,blank=True)
    respostaQuestao7 = models.CharField(max_length=100,blank=True)
    respostaQuestao8 = models.CharField(max_length=100,blank=True)
    respostaQuestao9 = models.CharField(max_length=100,blank=True)
    respostaQuestao10 = models.CharField(max_length=100,blank=True)
    class Meta:
        db_table = "resposta_formulario"
    



@receiver(pre_save, sender=EnviarArquivo)
def sobrescrever_arquivo(sender, **kwargs):
    verificar_pasta = kwargs['instance']
    try:

        print("verificar_pasta: ",verificar_pasta)
        if verificar_pasta.arquivo:
            arquivo_igual = verificar_pasta.arquivo.path
            print("Arquivo substituido com sucesso")
            os.remove(arquivo_igual)
    except FileNotFoundError:
        print("")

def data_valida(data):
    if data > datetime.now().date() - relativedelta(years=18) or data < datetime.now().date() - relativedelta(years=100):
        raise ValidationError("Insira uma data válida")

identity = (("students", "students"),
            ("teachers", "teachers"),
            ("Admin", "Admin"))

class Professor(models.Model):
    Usuario = models.OneToOneField(User, on_delete=models.CASCADE,default="")
    idProfessor = models.AutoField(primary_key = True)
    Nome = models.CharField(max_length=50, blank=True)
    Email = models.EmailField()
    Nascimento = models.DateField(default=date.today,blank=True,help_text=('Insira uma data que seja menor que 18 e maior que 100 anos atrás'),validators=[data_valida])
    Materia = models.CharField(max_length=50,blank=False,default="",help_text=('Entrar no SAE como professor'))
    isProf = models.BooleanField(default=0) 
    @property
    def esta_ativo(self):
            return bool(self.isProf)  
    class Meta:
        db_table = "Professor"

User._meta.get_field('username').validators=[validators.RegexValidator(r'^[\w.@+ ]+$', _('Digite um nome válido.'), 'Inválido')]
