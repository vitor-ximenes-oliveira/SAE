from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
import os
from datetime import *
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError

class Aluno(models.Model):
    ra = models.AutoField(primary_key = True)
    al_nome = models.CharField(max_length=100,blank=False)
    al_email = models.EmailField()
    al_senha = models.CharField(max_length=100)
    al_nascimento = models.DateField(default=date.today) 
    class Meta:
        db_table = "Aluno"        
    def __str__(self):
        return str(self.ra)

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

class Professor_Materias(models.Model):
    idMaterias = models.AutoField(primary_key = True)
    nome_materia = models.CharField(max_length=30)
    id_prof = models.ForeignKey('Professor',on_delete=models.CASCADE)
    class Meta:
        db_table = 'professor_materias'

OPCOES = [
        ('ruim','Ruim'),
        ('bom','Bom'),
        ('médio','Médio'),
        ('excelente','Excelente'),
]

class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    pergunta1 = models.CharField(max_length=10,choices=OPCOES, blank=True)
    justificativa1 = models.CharField(max_length=255,blank = True)
    pergunta2 = models.CharField(max_length=10, choices=OPCOES,blank = True)
    justificativa2 = models.CharField(max_length=255,blank = True)
    pergunta3 = models.CharField(max_length=10, choices=OPCOES,blank = True)
    justificativa3 = models.CharField(max_length=255,blank = True)
    pergunta4 = models.CharField(max_length=10, choices=OPCOES,blank = True)
    justificativa4 = models.CharField(max_length=255,blank = True)
    pergunta5 = models.CharField(max_length=10, choices=OPCOES,blank = True)
    justificativa5 = models.CharField(max_length=255,blank = True)
    pergunta6 = models.CharField(max_length=10, choices=OPCOES,blank = True)
    justificativa6 = models.CharField(max_length=255,blank = True)
    pergunta7 = models.CharField(max_length=10, choices=OPCOES,blank = True)
    justificativa7 = models.CharField(max_length=255,blank = True)
    pergunta8 = models.CharField(max_length=10, choices=OPCOES,blank = True)
    justificativa8 = models.CharField(max_length=255,blank = True)
    pergunta9 = models.CharField(max_length=10, choices=OPCOES,blank = True)
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

@receiver(pre_save, sender=EnviarArquivo)
def sobrescrever_arquivo(sender, **kwargs):
    verificar_pasta = kwargs['instance']
    try:
        if verificar_pasta.arquivo:
            arquivo_igual = verificar_pasta.arquivo.path
            os.remove(arquivo_igual)
    except FileNotFoundError:
            print("")

def data_valida(data):
    if data > datetime.now().date() - relativedelta(years=18) or data < datetime.now().date() - relativedelta(years=100):
        raise ValidationError("Insira uma data válida")

class Professor(models.Model):
    Usuario = models.OneToOneField(User, on_delete=models.CASCADE,default="")
    idProfessor = models.AutoField(primary_key = True)
    pf_nome = models.CharField(max_length=50, blank=True)
    pf_email = models.EmailField()
    pf_nascimento = models.DateField(default=date.today,blank=True,help_text=('Insira uma data que seja menor que 18 e maior que 100 anos atrás'),validators=[data_valida])
    materia = models.CharField(max_length=50,blank=False,default="")
    isProf = models.BooleanField(default=1) 
    @property
    def esta_ativo(self):
            return bool(self.isProf)  
    class Meta:
        db_table = "Professor"

User._meta.get_field('username').validators=[validators.RegexValidator(r'^[\w.@+ ]+$', _('Digite um nome válido.'), 'Inválido')]
