from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import ModelForm, EmailInput

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'username',)
        widgets = {
            'email': EmailInput(attrs={'required': True, 'autofocus': True}),
        }


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'username')


class UserUpdateForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['email', 'username']
