from django.urls import path
from . import views

urlpatterns = [

    path('', views.job_list, name='job_list'),

    path('<int:pk>/', views.job_detail, name='job_detail'),
    path('<int:pk>/save/', views.toggle_saved_job, name='save_job'),

]
