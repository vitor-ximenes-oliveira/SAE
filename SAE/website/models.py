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
