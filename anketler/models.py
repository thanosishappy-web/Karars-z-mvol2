from django.db import models
from django.contrib.auth.models import User


class Anket(models.Model):
    """Kullanıcıların oluşturduğu anketler."""

    soru = models.CharField(
        max_length=300,
        verbose_name='Soru',
        help_text='Ne hakkında kararsızsın? (en az 10 karakter)'
    )
    olusturan = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='anketler',
        verbose_name='Oluşturan'
    )
    olusturma_tarihi = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Oluşturma Tarihi'
    )
    aktif = models.BooleanField(
        default=True,
        verbose_name='Aktif'
    )

    class Meta:
        verbose_name = 'Anket'
        verbose_name_plural = 'Anketler'
        ordering = ['-olusturma_tarihi']

    def __str__(self):
        return self.soru[:80]

    @property
    def toplam_oy(self):
        """Anketteki toplam oy sayısını döndürür."""
        return sum(secenek.oy_sayisi for secenek in self.secenekler.all())


class Secenek(models.Model):
    """Bir ankete ait seçenekler."""

    anket = models.ForeignKey(
        Anket,
        on_delete=models.CASCADE,
        related_name='secenekler',
        verbose_name='Anket'
    )
    metin = models.CharField(
        max_length=200,
        verbose_name='Seçenek Metni'
    )
    oy_sayisi = models.PositiveIntegerField(
        default=0,
        verbose_name='Oy Sayısı'
    )

    class Meta:
        verbose_name = 'Seçenek'
        verbose_name_plural = 'Seçenekler'

    def __str__(self):
        return f"{self.metin} ({self.oy_sayisi} oy)"

    @property
    def oy_yuzdesi(self):
        """Bu seçeneğin toplam oy içindeki yüzdesini döndürür."""
        toplam = self.anket.toplam_oy
        if toplam == 0:
            return 0
        return round((self.oy_sayisi / toplam) * 100)


class Oy(models.Model):
    """Kullanıcıların verdiği oylar."""

    secenek = models.ForeignKey(
        Secenek,
        on_delete=models.CASCADE,
        related_name='oylar',
        verbose_name='Seçenek'
    )
    anket = models.ForeignKey(
        Anket,
        on_delete=models.CASCADE,
        related_name='oylar',
        verbose_name='Anket'
    )
    oturum_id = models.CharField(
        max_length=64,
        verbose_name='Oturum ID',
        help_text='Anonim kullanıcılar için session key'
    )
    kullanici = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='oylar',
        verbose_name='Kullanıcı'
    )
    tarih = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Oy Tarihi'
    )

    class Meta:
        verbose_name = 'Oy'
        verbose_name_plural = 'Oylar'
        constraints = [
            # Aynı oturum aynı ankete sadece 1 kez oy verebilir
            models.UniqueConstraint(
                fields=['anket', 'oturum_id'],
                name='unique_oturum_oy'
            ),
        ]

    def __str__(self):
        kim = self.kullanici.username if self.kullanici else f"Anonim ({self.oturum_id[:8]})"
        return f"{kim} → {self.secenek.metin}"
