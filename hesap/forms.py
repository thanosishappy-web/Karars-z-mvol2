from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class KayitFormu(UserCreationForm):
    """Kullanıcı kayıt formu: kullanıcı adı, e-posta, şifre."""

    username = forms.CharField(
        max_length=30,
        min_length=3,
        label='Kullanıcı Adı',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'kullanici_adi',
            'autocomplete': 'username',
        }),
        help_text='3-30 karakter. Harf, rakam ve alt çizgi (_) kullanabilirsiniz.',
    )
    email = forms.EmailField(
        label='E-posta',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'ornek@email.com',
            'autocomplete': 'email',
        }),
    )
    password1 = forms.CharField(
        label='Şifre',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'autocomplete': 'new-password',
        }),
        help_text='En az 8 karakter.',
    )
    password2 = forms.CharField(
        label='Şifre (Tekrar)',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'autocomplete': 'new-password',
        }),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Bu e-posta adresi zaten kullanılıyor.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username.replace('_', '').isalnum():
            raise ValidationError('Kullanıcı adı sadece harf, rakam ve alt çizgi içerebilir.')
        return username


class GirisFormu(forms.Form):
    """Kullanıcı giriş formu: kullanıcı adı veya e-posta + şifre."""

    giris_bilgisi = forms.CharField(
        label='Kullanıcı Adı veya E-posta',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'kullanici_adi veya ornek@email.com',
            'autocomplete': 'username',
        }),
    )
    sifre = forms.CharField(
        label='Şifre',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
        }),
    )
