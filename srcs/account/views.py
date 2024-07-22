from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import RegisterForm, LoginForm, ProfileForm
from django.contrib.auth.decorators import login_required

import logging

logger = logging.getLogger(__name__)

@login_required
def profile_view(request):
    user = request.user
    edit_mode = request.GET.get('edit') == 'true'
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)
    return render(request, 'account/profile.html', {
        'form': form,
        'edit_mode': edit_mode,
    })


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save() 
            login(request, user, backend='account.backends.UserBackend')
            return redirect('profile')
    else:
        form = RegisterForm()
    return render(request, 'account/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user, backend='account.backends.UserBackend')
                return redirect('profile')
            else:
                form.add_error(None, 'Identifiants incorrects')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})