from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    home, UserLoginView, register, admin_dashboard,
    madre_dashboard, acudiente_dashboard, redirect_dashboard,
    lista_usuarios, crear_usuario, editar_usuario, eliminar_usuario,
    dashboard, configuration, user_profile, panel_acudiente,
    update_profile, change_password, publicaciones
)

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('madre_dashboard/', madre_dashboard, name='madre_dashboard'),
    path('acudiente_dashboard/', acudiente_dashboard,
         name='acudiente_dashboard'),
    path('redirect_dashboard/', redirect_dashboard,
         name='redirect_dashboard'),
    path('usuarios/', lista_usuarios, name='lista_usuarios'),
    path('usuarios/crear/', crear_usuario, name='crear_usuario'),
    path('usuarios/<int:pk>/editar/',
         editar_usuario, name='editar_usuario'),
    path('usuarios/<int:pk>/eliminar/',
         eliminar_usuario, name='eliminar_usuario'),
    path('profile/', user_profile, name='user_profile'),
    path('configuration/', configuration, name='configuration'),
    path('panel_acudiente/', panel_acudiente, name='panel_acudiente'),
    path('update_profile/', update_profile, name='update_profile'),
    path('change_password/', change_password, name='update_password'),
    path('nuevas_publicaciones/', publicaciones, name='nuevas_publicaciones'),
]
