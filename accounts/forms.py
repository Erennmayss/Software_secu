from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class SignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, label='Prenom')
    last_name = forms.CharField(max_length=50, required=True, label='Nom')
    email = forms.EmailField(required=True, label='Adresse e-mail')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Un compte avec cette adresse e-mail existe deja.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            password_validation.validate_password(password)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Adresse e-mail ou identifiant',
        widget=forms.TextInput(attrs={
            'placeholder': 'vous@exemple.com ou admin',
            'autofocus': True,
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.attrs['placeholder'] = '••••••••'
        self.error_messages['invalid_login'] = "Email, identifiant ou mot de passe incorrect."


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.exclude(pk=self.instance.pk).filter(email__iexact=email).exists():
            raise forms.ValidationError("Cette adresse e-mail est deja utilisee.")
        return email


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label='Ancien mot de passe')
    new_password = forms.CharField(widget=forms.PasswordInput, min_length=8, label='Nouveau mot de passe')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirmer')

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        old_password = cleaned.get('old_password')

        if old_password and not self.user.check_password(old_password):
            self.add_error('old_password', "L'ancien mot de passe est incorrect.")

        new_password = cleaned.get('new_password')
        if new_password:
            try:
                password_validation.validate_password(new_password, self.user)
            except ValidationError as error:
                self.add_error('new_password', error)

        if cleaned.get('new_password') != cleaned.get('confirm_password'):
            self.add_error('confirm_password', 'Les mots de passe ne correspondent pas.')
        return cleaned
