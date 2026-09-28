from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import KayitFormu, GirisFormu


def kayit_view(request):
    """Kullanıcı kayıt sayfası."""
    if request.user.is_authenticated:
        return redirect('anketler:anasayfa')

    if request.method == 'POST':
        form = KayitFormu(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Hoş geldin @{user.username}! Hesabın oluşturuldu. 🎉')
            return redirect('anketler:anasayfa')
    else:
        form = KayitFormu()

    return render(request, 'hesap/kayit.html', {'form': form})


def giris_view(request):
    """Kullanıcı giriş sayfası."""
    if request.user.is_authenticated:
        return redirect('anketler:anasayfa')

    if request.method == 'POST':
        form = GirisFormu(request.POST)
        if form.is_valid():
            giris_bilgisi = form.cleaned_data['giris_bilgisi']
            sifre = form.cleaned_data['sifre']

            # Kullanıcı adı veya e-posta ile giriş denemesi
            user = authenticate(request, username=giris_bilgisi, password=sifre)

            # E-posta ile deneme
            if user is None:
                try:
                    kullanici = User.objects.get(email=giris_bilgisi)
                    user = authenticate(request, username=kullanici.username, password=sifre)
                except User.DoesNotExist:
                    pass

            if user is not None:
                login(request, user)
                messages.success(request, f'Tekrar hoş geldin @{user.username}! 👋')
                # next parametresi varsa oraya yönlendir
                next_url = request.GET.get('next', 'anketler:anasayfa')
                return redirect(next_url)
            else:
                messages.error(request, 'Kullanıcı adı/e-posta veya şifre hatalı.')
    else:
        form = GirisFormu()

    return render(request, 'hesap/giris.html', {'form': form})


def cikis_view(request):
    """Kullanıcı çıkışı."""
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Başarıyla çıkış yaptın. Görüşmek üzere! 👋')
    return redirect('anketler:anasayfa')


@login_required
def profil_view(request):
    """Kullanıcı profil sayfası — kendi anketlerini listeler."""
    anketlerim = request.user.anketler.all().order_by('-olusturma_tarihi')
    return render(request, 'hesap/profil.html', {
        'anketlerim': anketlerim,
    })
