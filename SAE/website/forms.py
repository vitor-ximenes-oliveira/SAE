from django import forms
from website.models import Aluno

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = "__all__"
        widgets = { 'password': forms.PasswordInput()}