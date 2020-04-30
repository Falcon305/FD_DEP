from django import forms
from .models import Project


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('title', 'description', 'dataset')
