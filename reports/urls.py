from reports import views as reports_views
from django.urls import path

urlpatterns = [
    path('reportes/', reports_views.reportes_general, name='reportes_general'),
]