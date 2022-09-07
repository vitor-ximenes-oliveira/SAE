from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
import os

class Aluno(models.Model):
    ra = models.AutoField(primary_key = True)
    al_nome = models.CharField(max_length=100)
    al_email = models.EmailField()
    al_senha = models.CharField(max_length=100)
    al_nascimento = models.DateField()  
    class Meta:
        db_table = "Aluno"

class Professor(models.Model):
    idProfessor = models.AutoField(primary_key = True)
    pf_nome = models.CharField(max_length=100)
    pf_email = models.EmailField()
    pf_senha = models.CharField(max_length=100)
    pf_nascimento = models.DateField()
    isProf = models.BooleanField(default=1)
    pf_materia = models.CharField(max_length=100)

    @property
    def esta_ativo(self):
            return bool(self.isProf)
    class Meta:
        db_table = "Professor"
        
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

@receiver(pre_save, sender=EnviarArquivo)
def sobrescrever_arquivo(sender, **kwargs):
    verificar_pasta = kwargs['instance']
    print("verificar_pasta: ",verificar_pasta)
    if verificar_pasta.arquivo:
        arquivo_igual = verificar_pasta.arquivo.path
        print("Arquivo substituido com sucesso")
        os.remove(arquivo_igual)

User._meta.get_field('username')._unique = True
