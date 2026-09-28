from django.contrib import admin
from .models import Anket, Secenek, Oy


class SecenekInline(admin.TabularInline):
    """Anket admin sayfasında seçenekleri inline olarak gösterir."""
    model = Secenek
    extra = 2
    min_num = 2
    max_num = 5


@admin.register(Anket)
class AnketAdmin(admin.ModelAdmin):
    list_display = ('soru', 'olusturan', 'olusturma_tarihi', 'aktif', 'toplam_oy_goster')
    list_filter = ('aktif', 'olusturma_tarihi')
    search_fields = ('soru', 'olusturan__username')
    date_hierarchy = 'olusturma_tarihi'
    inlines = [SecenekInline]

    @admin.display(description='Toplam Oy')
    def toplam_oy_goster(self, obj):
        return obj.toplam_oy


@admin.register(Secenek)
class SecenekAdmin(admin.ModelAdmin):
    list_display = ('metin', 'anket', 'oy_sayisi')
    list_filter = ('anket',)
    search_fields = ('metin',)


@admin.register(Oy)
class OyAdmin(admin.ModelAdmin):
    list_display = ('anket', 'secenek', 'kullanici', 'oturum_id', 'tarih')
    list_filter = ('tarih',)
    search_fields = ('kullanici__username', 'oturum_id')
    readonly_fields = ('tarih',)
