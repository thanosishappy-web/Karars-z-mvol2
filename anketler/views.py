from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, F
from .models import Anket, Secenek, Oy
from .forms import AnketOlusturFormu


def _get_oturum_id(request):
    """Kullanıcının oturum ID'sini döndürür. Session yoksa oluşturur."""
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _kullanici_oy_verdi_mi(request, anket):
    """Kullanıcının bu ankete daha önce oy verip vermediğini kontrol eder."""
    oturum_id = _get_oturum_id(request)
    return Oy.objects.filter(anket=anket, oturum_id=oturum_id).exists()


def _kullanici_oyu(request, anket):
    """Kullanıcının bu anketteki oyunu döndürür (varsa)."""
    oturum_id = _get_oturum_id(request)
    try:
        return Oy.objects.get(anket=anket, oturum_id=oturum_id)
    except Oy.DoesNotExist:
        return None


def anasayfa_view(request):
    """Ana sayfa — tüm aktif anketleri listeler."""
    anket_listesi = Anket.objects.filter(aktif=True).select_related('olusturan').prefetch_related('secenekler')

    # Her anket için kullanıcının oy verip vermediğini kontrol et
    oturum_id = _get_oturum_id(request)
    oylanan_anket_idler = set(
        Oy.objects.filter(oturum_id=oturum_id).values_list('anket_id', flat=True)
    )

    paginator = Paginator(anket_listesi, 10)
    sayfa_no = request.GET.get('sayfa', 1)
    anketler = paginator.get_page(sayfa_no)

    return render(request, 'anketler/anasayfa.html', {
        'anketler': anketler,
        'oylanan_anket_idler': oylanan_anket_idler,
    })


def anket_detay_view(request, pk):
    """Anket detay sayfası — seçenekler + oylama veya sonuçlar."""
    anket = get_object_or_404(
        Anket.objects.select_related('olusturan').prefetch_related('secenekler'),
        pk=pk
    )

    oy_verildi = _kullanici_oy_verdi_mi(request, anket)
    kullanici_oyu = _kullanici_oyu(request, anket) if oy_verildi else None

    return render(request, 'anketler/anket_detay.html', {
        'anket': anket,
        'oy_verildi': oy_verildi,
        'kullanici_oyu': kullanici_oyu,
    })


@login_required
def anket_olustur_view(request):
    """Yeni anket oluşturma."""
    if request.method == 'POST':
        form = AnketOlusturFormu(request.POST)
        if form.is_valid():
            # Anketi oluştur
            anket = Anket.objects.create(
                soru=form.cleaned_data['soru'],
                olusturan=request.user,
            )
            # Seçenekleri oluştur
            for metin in form.get_secenekler():
                Secenek.objects.create(anket=anket, metin=metin)

            messages.success(request, 'Anketin başarıyla oluşturuldu! 🎉')
            return redirect('anketler:detay', pk=anket.pk)
    else:
        form = AnketOlusturFormu()

    return render(request, 'anketler/anket_olustur.html', {'form': form})


def oyla_view(request, pk):
    """Ankete oy ver — AJAX POST endpoint'i."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Sadece POST istekleri kabul edilir.'}, status=405)

    anket = get_object_or_404(Anket, pk=pk, aktif=True)
    oturum_id = _get_oturum_id(request)

    # Mükerrer oy kontrolü
    if Oy.objects.filter(anket=anket, oturum_id=oturum_id).exists():
        return JsonResponse({'error': 'Bu ankete zaten oy verdin!'}, status=400)

    # Seçenek ID'sini al
    secenek_id = request.POST.get('secenek_id')
    if not secenek_id:
        return JsonResponse({'error': 'Bir seçenek seçmelisin.'}, status=400)

    try:
        secenek = Secenek.objects.get(pk=secenek_id, anket=anket)
    except Secenek.DoesNotExist:
        return JsonResponse({'error': 'Geçersiz seçenek.'}, status=400)

    # Oyu kaydet
    Oy.objects.create(
        secenek=secenek,
        anket=anket,
        oturum_id=oturum_id,
        kullanici=request.user if request.user.is_authenticated else None,
    )

    # Oy sayısını güncelle
    secenek.oy_sayisi = F('oy_sayisi') + 1
    secenek.save(update_fields=['oy_sayisi'])

    # Güncel sonuçları döndür
    anket.refresh_from_db()
    secenekler = anket.secenekler.all()
    toplam_oy = sum(s.oy_sayisi for s in secenekler)

    sonuclar = []
    for s in secenekler:
        yuzde = round((s.oy_sayisi / toplam_oy) * 100) if toplam_oy > 0 else 0
        sonuclar.append({
            'id': s.pk,
            'metin': s.metin,
            'oy_sayisi': s.oy_sayisi,
            'yuzde': yuzde,
            'secildi': s.pk == secenek.pk,
        })

    return JsonResponse({
        'success': True,
        'toplam_oy': toplam_oy,
        'sonuclar': sonuclar,
    })
