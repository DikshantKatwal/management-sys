from django.urls import path
from . import views
urlpatterns = [
    path("register/customer/", views.CustomerRegisterView.as_view(), name="register-customer"),
    path("register/employee/", views.EmployeeRegisterView.as_view(), name="register-employee"),

    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),

    path("me/", views.UserAPIView.as_view(), name="me"),
    path("refresh/", views.CookieTokenRefreshView.as_view(), name="cookie-refresh"),
]
