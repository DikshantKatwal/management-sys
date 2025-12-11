from django.urls import path, include

urlpatterns = [
    path("user/", include("apps.users.urls")),
    path("room/", include("apps.rooms.urls")),
    path("check-in/", include("apps.check_ins.urls")),
    path("customer/", include("apps.customers.urls")),
    path("employee/", include("apps.employees.urls")),

]
