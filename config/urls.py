"""
TR: Ana URL yönlendirmeleri.
ES: Rutas URL principales.
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

# TR: Yönetim paneli başlıkları (Türkçe)
# ES: Títulos del panel de administración (en turco)
admin.site.site_header = "KampüsRez Yönetim Paneli"
admin.site.site_title = "KampüsRez"
admin.site.index_title = "Yönetim"

urlpatterns = [
    path("admin/", admin.site.urls),
    # TR: Geçici ana sayfa — ilerleyen sprintlerde gerçek görünümlerle değiştirilecek
    # ES: Página de inicio temporal — se sustituirá por vistas reales en los próximos sprints
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
]
