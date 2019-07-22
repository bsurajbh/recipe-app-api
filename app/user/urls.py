from django.urls import path
from user import views

app_name = 'user'

urlpatterns = [
    path('create/', views.createUseriew.as_view(), name='create'),
    path('token/', views.createTokenView.as_view(), name='token'),
    path('user/', views.ManageUserView.as_view(), name='user'),
]
