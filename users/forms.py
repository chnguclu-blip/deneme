from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'w-full border-gray-300 rounded-lg'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'w-full border-gray-300 rounded-lg'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'w-full border-gray-300 rounded-lg'}))
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'groups')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full border-gray-300 rounded-lg'}),
        }

class CustomUserChangeForm(UserChangeForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'w-full border-gray-300 rounded-lg'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'w-full border-gray-300 rounded-lg'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'w-full border-gray-300 rounded-lg'}))
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)
    password = None # Don't allow password change here for simplicity, use Admin or separate form

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser', 'groups')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full border-gray-300 rounded-lg'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'mr-2'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'mr-2'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'mr-2'}),
        }

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border-gray-300 rounded-lg'}),
        }
