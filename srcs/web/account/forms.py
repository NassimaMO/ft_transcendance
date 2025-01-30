# accounts/forms.py
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import ModelForm
from .models import User

class RegisterForm(UserCreationForm):

    class Meta(UserCreationForm.Meta) :
        model = User
        fields = ('username', 'password1', 'password2')

class LoginForm(AuthenticationForm):

    class Meta :
        model = User
        fields = ('username', 'password')

class ProfileForm(ModelForm):

    class Meta:
        model = User
        fields = ('username', 'avatar', 'status')