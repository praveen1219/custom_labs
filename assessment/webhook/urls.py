from django.urls import path
from . import views

urlpatterns = [
    path('account/', views.create_account, name='create_account'),
    path('destination/', views.create_destination, name='create_destination'),
    path('destinations/<str:account_id>/', views.get_destinations, name='get_destinations'),
    path('account/<str:account_id>/', views.delete_account, name='delete_account'),
    path('server/incoming_data/', views.incoming_data, name='incoming_data'),
]
