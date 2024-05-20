from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import AppConfig


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UploadFileForm(forms.Form):
    input_file = forms.FileField(required=True,label='Select a csv file')
    output_file = forms.CharField(max_length=100, required=False)
    
class RegexForm(forms.Form):
    search_regex = forms.CharField(max_length=100, required=True)
    replace_regex = forms.CharField(max_length=100, required=False)
    output_file = forms.CharField(max_length=100, required=False)

class AppConfigForm(forms.ModelForm):
    host = forms.CharField(max_length=100, required=True)
    tls_enabled = forms.BooleanField
    access_token = forms.CharField(max_length=255, required=True)
    
    class Meta:
        model = AppConfig
        fields = ['host', 'tls_enabled', 'access_token']
        