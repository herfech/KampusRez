"""
TR: Ana URL yönlendirmeleri. Adresler kullanıcıya göründüğü için Türkçedir.
ES: Rutas URL principales. Las direcciones están en turco porque las ve el usuario.
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

# TR: Yönetim paneli başlıkları (Türkçe)
# ES: Títulos del panel de administración (en turco)
admin.site.site_header = "KampüsRez Yönetim Paneli"
admin.site.site_title = "KampüsRez"
admin.site.index_title = "Yönetim"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("hesap/", include("accounts.urls")),
    path("alanlar/", include("spaces.urls")),
    path("rezervasyonlarim/", include("reservations.urls")),
]
