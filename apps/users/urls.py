from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'register/employees', views.EmployeeRegisterView)

urlpatterns = [
    path("register/guest/", views.GuestRegisterView.as_view(), name="register-guest"),
    # path("register/employee/", views.EmployeeRegisterView.as_view(), name="register-employee"),

    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),

    path("me/", views.UserAPIView.as_view(), name="me"),
    path("refresh/", views.CookieTokenRefreshView.as_view(), name="cookie-refresh"),
]




urlpatterns = urlpatterns + router.urls