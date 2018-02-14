from django import forms
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=("username","password","email","is_superuser","is_active","date_joined","last_login")