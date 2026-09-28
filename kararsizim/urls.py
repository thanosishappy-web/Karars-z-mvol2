"""
URL configuration for kararsizim project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hesap/', include('hesap.urls')),
    path('', include('anketler.urls')),
]
