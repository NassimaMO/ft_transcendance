from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import RegisterForm, LoginForm, ProfileForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from urllib.parse import urlencode


def login_view(request):
    next_url = request.GET.get('next', None)
    if request.user.is_authenticated:
        if next_url:
            return redirect(next_url)
        return redirect('profile') 
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user, backend='account.backends.UserBackend')
                if next_url:
                    return redirect(next_url)
                return redirect('profile')
            else:
                form.add_error(None, 'Identifiants incorrects')
    else:
        form = LoginForm()
    register_url = reverse('register')
    if next_url:
        register_url = f'{register_url}?{urlencode({"next": next_url})}'
    return render(request, 'account/login.html', {'form': form, 'register_url': register_url})


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
    next_url = request.GET.get('next', None)
    if request.user.is_authenticated:
        if next_url:
            return redirect(next_url)
        return redirect('profile')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user, backend='account.backends.UserBackend')
            if next_url:
                return redirect(next_url)
            return redirect('profile')
    else:
        form = RegisterForm()
    return render(request, 'account/register.html', {'form': form, 'next': next_url})


def logout_view(request):
    if request.user.is_authenticated :
        logout(request)
        return redirect('login')
    return login_view(request)
