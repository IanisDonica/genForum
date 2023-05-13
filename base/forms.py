from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import User, Post

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('name','email', 'password1', 'password2')

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['name', 'content']

class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'background']