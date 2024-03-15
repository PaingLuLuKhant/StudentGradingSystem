# api/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index , name='index'),
    # .as_view() is for class-based views -it converts to function-based view
    
    # path('login/', views.login_view, name="login_view"),
    # path('admin_panel/', views.admin_panel , name="admin_panel"),

    path('all_students/<input>/' ,views.all_students, name='all_students'),
    path('specific_student/<input>/' ,views.specific_student, name='specific_student'),
    path('get_student_by_cgpa/<input>/' ,views.get_student_by_cgpa, name='get_student_by_cgpa'),
    path('get_student_by_cgpa_and_major/<input>/' ,views.get_student_by_cgpa_and_major, name='get_student_by_cgpa_and_major'),
    path('excel_export', views.export_students_to_excel, name='excel_export'),
    #grade fetch paths
    path('getStudentGrades/<input>/' ,views.getStudentGrades, name='getStudentGrades'),
    
    # log in authentication paths
    path('signin' , views.signin , name ="signin"),
    path('admin_home/', views.admin_home, name='admin_home'),
    path('signout' , views.signout , name ="signout"),
    
    # recommmendation paths
    
    path('recommendation/<input>/' , views.recommendation , name ='recommendation'),
]