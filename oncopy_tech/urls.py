from django.urls import path
from . import views

app_name = 'oncopy_tech'

urlpatterns = [
    path('', views.index, name='index'),
    path('submit-request/', views.submit_request, name='submit_request'),
]
