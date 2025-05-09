from django.shortcuts import render , redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import User
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')  # Redirect to a success page.
        else:
            # Return an 'invalid login' error message.
            return render(request, 'users/login.html', {'error': 'Invalid username or password.'})
    return render(request, 'users/login.html')


@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'users/profile.html', {'user': user})
