from django import forms
from .models import Anket


class AnketOlusturFormu(forms.Form):
    """Yeni anket oluşturma formu: soru + 2-5 seçenek."""

    soru = forms.CharField(
        max_length=300,
        min_length=10,
        label='Ne hakkında kararsızsın?',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Bugün sinemaya mı gitsem yoksa restorana mı?',
            'autofocus': True,
        }),
    )

    secenek_1 = forms.CharField(
        max_length=200,
        label='Seçenek 1',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Sinema',
        }),
    )

    secenek_2 = forms.CharField(
        max_length=200,
        label='Seçenek 2',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Restoran',
        }),
    )

    secenek_3 = forms.CharField(
        max_length=200,
        required=False,
        label='Seçenek 3',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Opsiyonel...',
        }),
    )

    secenek_4 = forms.CharField(
        max_length=200,
        required=False,
        label='Seçenek 4',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Opsiyonel...',
        }),
    )

    secenek_5 = forms.CharField(
        max_length=200,
        required=False,
        label='Seçenek 5',
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Opsiyonel...',
        }),
    )

    def get_secenekler(self):
        """Dolu olan seçenekleri liste olarak döndürür."""
        secenekler = []
        for i in range(1, 6):
            metin = self.cleaned_data.get(f'secenek_{i}', '').strip()
            if metin:
                secenekler.append(metin)
        return secenekler
