from django.urls import path, include

urlpatterns = [
    path("user/", include("apps.users.urls")),
    path("room/", include("apps.rooms.urls")),
    path("stays/", include("apps.stays.urls")),
    path("guest/", include("apps.guests.urls")),
    path("employee/", include("apps.employees.urls")),

]
