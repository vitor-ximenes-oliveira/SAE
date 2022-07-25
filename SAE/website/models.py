from django.db import models

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

    @property
    def esta_ativo(self):
            return bool(self.isProf)
    class Meta:
        db_table = "Professor"

OPCOES = [
        ('ruim','Ruim'),
        ('bom','Bom'),
        ('médio','Médio'),
        ('excelente','Excelente'),
]

class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    pergunta1 = models.CharField(max_length=10,choices=OPCOES, blank=False)
    justificativa1 = models.CharField(max_length=255,blank = False)
    pergunta2 = models.CharField(max_length=10, choices=OPCOES,blank = False)
    justificativa2 = models.CharField(max_length=255,blank = False)
    pergunta3 = models.CharField(max_length=10, choices=OPCOES,blank = False)
    justificativa3 = models.CharField(max_length=255,blank = False)
    pergunta4 = models.CharField(max_length=10, choices=OPCOES,blank = False)
    justificativa4 = models.CharField(max_length=255,blank = False)
    pergunta5 = models.CharField(max_length=10, choices=OPCOES,blank = False)
    justificativa5 = models.CharField(max_length=255,blank = False)
    pergunta6 = models.CharField(max_length=10, choices=OPCOES,blank = False)
    justificativa6 = models.CharField(max_length=255,blank = False)
    pergunta7 = models.CharField(max_length=10, choices=OPCOES,blank = False)
    justificativa7 = models.CharField(max_length=255,blank = False)
    pergunta8 = models.CharField(max_length=10, choices=OPCOES,blank = False)
    justificativa8 = models.CharField(max_length=255,blank = False)
    pergunta9 = models.CharField(max_length=10, choices=OPCOES,blank = False)
    justificativa9 = models.CharField(max_length=255,blank = False)
    class Meta:
        db_table = "feedback"        
