"""
TR: Uygulamalar arasında ortak kullanılan erişim kontrolleri.
ES: Controles de acceso compartidos entre las aplicaciones.
"""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def manager_required(view):
    """
    TR: Sadece yönetici rolündeki kullanıcılar (veya süper kullanıcı) erişebilir; diğerleri 403 alır.
    ES: Solo pueden acceder los usuarios con rol administrador (o superusuario); el resto recibe un 403.
    """
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.can_manage_reservations:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper
