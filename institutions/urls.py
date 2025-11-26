from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_institutions, name='lista_institutions'),
    path('crear/', views.crear_institution, name='crear_institution'),
    path('<int:pk>/editar/', views.editar_institution, name='editar_institution'),
    path('<int:pk>/eliminar/', views.eliminar_institution, name='eliminar_institution'),
]
