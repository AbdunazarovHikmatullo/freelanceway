from django import forms
from .models import Vacancy, Application


class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = ['title', 'description', 'category', 'budget_min', 'budget_max', 'deadline', 'required_skills']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 5}),
            'required_skills': forms.TextInput(attrs={'placeholder': 'Например: Python, Django, JavaScript'}),
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter', 'proposed_budget', 'estimated_time']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Расскажите, почему вы подходите для этого проекта'}),
            'estimated_time': forms.TextInput(attrs={'placeholder': 'Например: 2 недели'}),
        }