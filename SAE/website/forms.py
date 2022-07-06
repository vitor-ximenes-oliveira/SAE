from django import forms
from website.models import Aluno, Professor

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = "__all__"       
        widgets = {'al_senha': forms.PasswordInput()}

class ProfessorForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = "__all__"
        widgets = {'pf_senha': forms.PasswordInput()}
