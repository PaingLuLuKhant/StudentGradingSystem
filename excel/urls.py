from django.urls import path
from . import views

urlpatterns = [
    path('excel_import/', views.upload_excel, name="excel_import"),
    path('export_enrollment_data/', views.export_enrollment_data, name='export_enrollment_data'),
]