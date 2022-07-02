from django.db import models

class Aluno(models.Model):
    id = models.AutoField(primary_key = True)
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    senha = models.CharField(max_length=100)
    class Meta:
        db_table = "aluno"
