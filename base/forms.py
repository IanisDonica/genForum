from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import User, Post
from django import forms

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


class BadgeAddForm(forms.Form):
    badge_type = forms.ChoiceField(choices=[], widget=forms.RadioSelect)
    badge_duration = forms.IntegerField()

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['badge_type'].choices = self.get_choices(user)

    def get_choices(self, user):
        from .models import BadgeType

        try:
            user_badge_types = user.badge_set.values_list('badge_type')
            badges = BadgeType.objects.filter(pk__in=user_badge_types)
            return BadgeType.objects.values_list("id","name").difference(badges)
        except:
            return BadgeType.objects.values_list("id","name")