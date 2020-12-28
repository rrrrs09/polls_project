from django.urls import path

from .views import UserCreateView, LoginView, LogoutView

urlpatterns = [
    path('user/', UserCreateView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view())
]
