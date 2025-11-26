from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.lista_students, name='lista_students'),
    path('crear/', views.crear_student, name='crear_student'),
    path('<int:pk>/editar/', views.editar_student, name='editar_student'),
    path('<int:pk>/eliminar/', views.eliminar_student, name='eliminar_student'),
    path('asistencia/', views.asistencia, name='asistencia'),
    path('registrar-asistencia/', views.registrar_asistencia,
         name='registrar_asistencia'),
    path('avance-academico/', views.avance_academico, name='avance_academico'),
]
