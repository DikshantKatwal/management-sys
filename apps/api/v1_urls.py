from django.urls import path, include

urlpatterns = [
    path("user/", include("apps.users.urls")),
    path("room/", include("apps.rooms.urls")),
    # path("check-in/", include("apps.check_ins.urls")),
    path("guest/", include("apps.guests.urls")),
    path("employee/", include("apps.employees.urls")),

]
