from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    path("register/customer/", views.CustomerRegisterView.as_view(), name="register-customer"),
    path("register/employee/", views.EmployeeRegisterView.as_view(), name="register-employee"),

    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("me/", views.UserAPIView.as_view(), name="me"),

]
