# Generated by Django 3.2.13 on 2022-10-11 17:34

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import website.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Aluno',
            fields=[
                ('ra', models.AutoField(primary_key=True, serialize=False)),
                ('al_nome', models.CharField(max_length=100)),
                ('al_email', models.EmailField(max_length=254)),
                ('al_senha', models.CharField(max_length=100)),
                ('al_nascimento', models.DateField()),
                ('isProf', models.BooleanField(default=0)),
            ],
            options={
                'db_table': 'Aluno',
            },
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('pergunta1', models.CharField(choices=[('ruim', 'Ruim'), ('bom', 'Bom'), ('médio', 'Médio'), ('excelente', 'Excelente')], max_length=10)),
                ('justificativa1', models.CharField(blank=True, max_length=255)),
                ('pergunta2', models.CharField(choices=[('ruim', 'Ruim'), ('bom', 'Bom'), ('médio', 'Médio'), ('excelente', 'Excelente')], max_length=10)),
                ('justificativa2', models.CharField(blank=True, max_length=255)),
                ('pergunta3', models.CharField(choices=[('ruim', 'Ruim'), ('bom', 'Bom'), ('médio', 'Médio'), ('excelente', 'Excelente')], max_length=10)),
                ('justificativa3', models.CharField(blank=True, max_length=255)),
                ('pergunta4', models.CharField(choices=[('ruim', 'Ruim'), ('bom', 'Bom'), ('médio', 'Médio'), ('excelente', 'Excelente')], max_length=10)),
                ('justificativa4', models.CharField(blank=True, max_length=255)),
                ('pergunta5', models.CharField(choices=[('ruim', 'Ruim'), ('bom', 'Bom'), ('médio', 'Médio'), ('excelente', 'Excelente')], max_length=10)),
                ('justificativa5', models.CharField(blank=True, max_length=255)),
                ('pergunta6', models.CharField(choices=[('ruim', 'Ruim'), ('bom', 'Bom'), ('médio', 'Médio'), ('excelente', 'Excelente')], max_length=10)),
                ('justificativa6', models.CharField(blank=True, max_length=255)),
                ('pergunta7', models.CharField(choices=[('ruim', 'Ruim'), ('bom', 'Bom'), ('médio', 'Médio'), ('excelente', 'Excelente')], max_length=10)),
                ('justificativa7', models.CharField(blank=True, max_length=255)),
                ('pergunta8', models.CharField(choices=[('ruim', 'Ruim'), ('bom', 'Bom'), ('médio', 'Médio'), ('excelente', 'Excelente')], max_length=10)),
                ('justificativa8', models.CharField(blank=True, max_length=255)),
                ('pergunta9', models.CharField(choices=[('ruim', 'Ruim'), ('bom', 'Bom'), ('médio', 'Médio'), ('excelente', 'Excelente')], max_length=10)),
                ('justificativa9', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'db_table': 'feedback',
            },
        ),
        migrations.CreateModel(
            name='Formulario',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('questao1', models.CharField(blank=True, max_length=200)),
                ('alternativaAquestao1', models.CharField(blank=True, max_length=100)),
                ('alternativaBquestao1', models.CharField(blank=True, max_length=100)),
                ('alternativaCquestao1', models.CharField(blank=True, max_length=100)),
                ('alternativaDquestao1', models.CharField(blank=True, max_length=100)),
                ('questao2', models.CharField(blank=True, max_length=200)),
                ('alternativaAquestao2', models.CharField(blank=True, max_length=100)),
                ('alternativaBquestao2', models.CharField(blank=True, max_length=100)),
                ('alternativaCquestao2', models.CharField(blank=True, max_length=100)),
                ('alternativaDquestao2', models.CharField(blank=True, max_length=100)),
                ('questao3', models.CharField(blank=True, max_length=200)),
                ('alternativaAquestao3', models.CharField(blank=True, max_length=100)),
                ('alternativaBquestao3', models.CharField(blank=True, max_length=100)),
                ('alternativaCquestao3', models.CharField(blank=True, max_length=100)),
                ('alternativaDquestao3', models.CharField(blank=True, max_length=100)),
                ('questao4', models.CharField(blank=True, max_length=200)),
                ('alternativaAquestao4', models.CharField(blank=True, max_length=100)),
                ('alternativaBquestao4', models.CharField(blank=True, max_length=100)),
                ('alternativaCquestao4', models.CharField(blank=True, max_length=100)),
                ('alternativaDquestao4', models.CharField(blank=True, max_length=100)),
                ('questao5', models.CharField(blank=True, max_length=200)),
                ('alternativaAquestao5', models.CharField(blank=True, max_length=100)),
                ('alternativaBquestao5', models.CharField(blank=True, max_length=100)),
                ('alternativaCquestao5', models.CharField(blank=True, max_length=100)),
                ('alternativaDquestao5', models.CharField(blank=True, max_length=100)),
                ('questao6', models.CharField(blank=True, max_length=200)),
                ('alternativaAquestao6', models.CharField(blank=True, max_length=100)),
                ('alternativaBquestao6', models.CharField(blank=True, max_length=100)),
                ('alternativaCquestao6', models.CharField(blank=True, max_length=100)),
                ('alternativaDquestao6', models.CharField(blank=True, max_length=100)),
                ('questao7', models.CharField(blank=True, max_length=200)),
                ('alternativaAquestao7', models.CharField(blank=True, max_length=100)),
                ('alternativaBquestao7', models.CharField(blank=True, max_length=100)),
                ('alternativaCquestao7', models.CharField(blank=True, max_length=100)),
                ('alternativaDquestao7', models.CharField(blank=True, max_length=100)),
                ('questao8', models.CharField(blank=True, max_length=200)),
                ('alternativaAquestao8', models.CharField(blank=True, max_length=100)),
                ('alternativaBquestao8', models.CharField(blank=True, max_length=100)),
                ('alternativaCquestao8', models.CharField(blank=True, max_length=100)),
                ('alternativaDquestao8', models.CharField(blank=True, max_length=100)),
                ('questao9', models.CharField(blank=True, max_length=200)),
                ('alternativaAquestao9', models.CharField(blank=True, max_length=100)),
                ('alternativaBquestao9', models.CharField(blank=True, max_length=100)),
                ('alternativaCquestao9', models.CharField(blank=True, max_length=100)),
                ('alternativaDquestao9', models.CharField(blank=True, max_length=100)),
                ('questao10', models.CharField(blank=True, max_length=200)),
                ('alternativaAquestao10', models.CharField(blank=True, max_length=100)),
                ('alternativaBquestao10', models.CharField(blank=True, max_length=100)),
                ('alternativaCquestao10', models.CharField(blank=True, max_length=100)),
                ('alternativaDquestao10', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao1', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao2', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao3', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao4', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao5', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao6', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao7', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao8', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao9', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao10', models.CharField(blank=True, max_length=100)),
            ],
            options={
                'db_table': 'formulario',
            },
        ),
        migrations.CreateModel(
            name='Professor',
            fields=[
                ('idProfessor', models.AutoField(primary_key=True, serialize=False)),
                ('Nome', models.CharField(blank=True, max_length=50)),
                ('Email', models.EmailField(max_length=254)),
                ('Nascimento', models.DateField(blank=True, default=datetime.date.today, help_text='Insira uma data que seja menor que 18 e maior que 100 anos atrás', validators=[website.models.data_valida])),
                ('Materia', models.CharField(default='', help_text='Entrar no SAE como professor', max_length=50)),
                ('isProf', models.BooleanField(default=1)),
                ('Usuario', models.OneToOneField(default='', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Professor',
            },
        ),
        migrations.CreateModel(
            name='questoesEscolhidasAluno',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('respostaQuestao1', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao2', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao3', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao4', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao5', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao6', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao7', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao8', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao9', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao10', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='RespostasFormulario',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('respostaQuestao1', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao2', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao3', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao4', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao5', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao6', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao7', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao8', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao9', models.CharField(blank=True, max_length=100)),
                ('respostaQuestao10', models.CharField(blank=True, max_length=100)),
            ],
            options={
                'db_table': 'resposta_formulario',
            },
        ),
        migrations.CreateModel(
            name='Turmas',
            fields=[
                ('idTurma', models.AutoField(primary_key=True, serialize=False)),
                ('ano_letivo', models.CharField(max_length=10)),
                ('classe', models.CharField(max_length=10)),
                ('alu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='website.aluno')),
                ('prof', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='website.professor')),
            ],
            options={
                'db_table': 'turmas',
            },
        ),
        migrations.CreateModel(
            name='EnviarArquivo',
            fields=[
                ('idEnvio', models.AutoField(primary_key=True, serialize=False)),
                ('arquivo', models.FileField(blank=True, null=True, upload_to='')),
                ('alu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.aluno')),
            ],
            options={
                'db_table': 'enviar_arquivo',
            },
        ),
        migrations.CreateModel(
            name='acertosErros',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('acertos', models.IntegerField()),
                ('aluno', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='website.aluno')),
            ],
        ),
    ]
