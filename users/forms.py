from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Форма для регистрации нового пользователя"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-input'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Имя пользователя', 'class': 'form-input'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Пароль', 'class': 'form-input'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Подтверждение пароля', 'class': 'form-input'})
    )
    user_type = forms.ChoiceField(
        choices=[('client', 'Я заказчик'), ('freelancer', 'Я фрилансер')],
        widget=forms.RadioSelect(attrs={'class': 'user-type-radio'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'user_type')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        # Устанавливаем тип пользователя
        user_type = self.cleaned_data.get('user_type')
        if user_type == 'client':
            user.is_client = True
        elif user_type == 'freelancer':
            user.is_freelancer = True
        
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Форма для входа пользователя"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Имя пользователя или Email', 'class': 'form-input'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Пароль', 'class': 'form-input'})
    )


class UserProfileForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя"""
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Имя', 'class': 'form-input'})
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Фамилия', 'class': 'form-input'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-input'})
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'О себе', 'class': 'form-textarea', 'rows': 4})
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Местоположение', 'class': 'form-input'})
    )
    website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'placeholder': 'Веб-сайт', 'class': 'form-input'})
    )
    github = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'placeholder': 'GitHub', 'class': 'form-input'})
    )
    twitter = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'placeholder': 'Twitter', 'class': 'form-input'})
    )
    linkedin = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'placeholder': 'LinkedIn', 'class': 'form-input'})
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-file-input'})
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'bio', 'location', 
                  'website', 'github', 'twitter', 'linkedin', 'avatar')


class CustomPasswordChangeForm(PasswordChangeForm):
    """Форма для изменения пароля"""
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Текущий пароль', 'class': 'form-input'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Новый пароль', 'class': 'form-input'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Подтверждение нового пароля', 'class': 'form-input'})
    )