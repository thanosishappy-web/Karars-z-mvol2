from django.urls import path
from . import views

app_name = 'anketler'

urlpatterns = [
    path('', views.anasayfa_view, name='anasayfa'),
    path('anket/<int:pk>/', views.anket_detay_view, name='detay'),
    path('anket/olustur/', views.anket_olustur_view, name='olustur'),
    path('anket/<int:pk>/oyla/', views.oyla_view, name='oyla'),
]
