from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_gateway, name='login_gateway'),
    path('employee/', views.employee, name='employee'),
    path('login/', views.login, name='login'),
    path('que_list/<int:survey_id>', views.question_list, name='que_list'),
    path('save/<int:survey_id>', views.save, name='save'),
    path('logout/', views.logout, name='logout'),
]
