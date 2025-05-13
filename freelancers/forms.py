from django import forms
from .models import Freelancer, Portfolio, Review, Category


class FreelancerProfileForm(forms.ModelForm):
    """Форма для создания и редактирования профиля фрилансера"""
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = Freelancer
        fields = [
            'headline', 'bio', 'skills', 'experience', 'hourly_rate', 
            'availability', 'telegram', 'whatsapp',
            'portfolio_url', 'education', 'certifications', 'categories'
        ]
        widgets = {
            'headline': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Например: Опытный веб-разработчик'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 5, 'placeholder': 'Расскажите о себе и своем опыте работы'}),
            'skills': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Например: Python, Django, JavaScript, React'}),
            'experience': forms.Select(attrs={'class': 'form-select'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'step': 100}),
            'availability': forms.Select(attrs={'class': 'form-select'}),
            'telegram': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '@username'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+7XXXXXXXXXX'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://'}),
            'education': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Укажите ваше образование'}),
            'certifications': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Перечислите ваши сертификаты и достижения'}),
        }


class PortfolioForm(forms.ModelForm):
    """Форма для добавления элемента портфолио"""
    class Meta:
        model = Portfolio
        fields = ['title', 'description', 'image', 'project_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Название проекта'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Описание проекта'}),
            'image': forms.FileInput(attrs={'class': 'form-file-input'}),
            'project_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://'}),
        }


class ReviewForm(forms.ModelForm):
    """Форма для добавления отзыва о фрилансере"""
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'rating-input'}),
            'comment': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Напишите ваш отзыв о работе фрилансера'}),
        }


class FreelancerFilterForm(forms.Form):
    """Форма для фильтрации фрилансеров"""
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Все категории",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    experience = forms.ChoiceField(
        choices=[('', 'Любой опыт')] + list(Freelancer.EXPERIENCE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    min_rating = forms.ChoiceField(
        choices=[('', 'Любой рейтинг')] + [(str(i), f"{i}+ звезд") for i in range(1, 6)],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    availability = forms.ChoiceField(
        choices=[('', 'Любая доступность')] + list(Freelancer.AVAILABILITY_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    skills = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Поиск по навыкам'})
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('rating', 'По рейтингу'),
            ('completed_projects', 'По количеству проектов'),
            ('hourly_rate', 'По возрастанию ставки'),
            ('-hourly_rate', 'По убыванию ставки'),
        ],
        required=False,
        initial='rating',
        widget=forms.Select(attrs={'class': 'form-select'})
    )