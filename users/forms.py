from django.contrib.auth.forms import UserCreationForm
from django.forms import Form, EmailField, EmailInput

from users.models import User


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control w-100', 'autocomplete': 'email'})
        self.fields['password1'].widget.attrs.update(
            {'class': 'form-control w-100', 'autocomplete': 'new-password'})
        self.fields['password2'].widget.attrs.update(
            {'class': 'form-control w-100', 'autocomplete': 'new-password'})


class PasswordResetRequestForm(Form):
    email = EmailField(widget=EmailInput(attrs={'class': 'form-control w-100', 'autocomplete': 'email'}))
