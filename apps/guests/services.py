from apps.guests.models import Guest
from apps.guests.serializers import GuestSerializer
from apps.users.models import User
from apps.users.serializers import UserSerializer


def create_update_guest(data, user: User | None = None):
    """
    Create or update User and Guest profile
    """

    # 1. Save User
    user_serializer = save_user(data=data, user=user)
    user = user_serializer.save()

    # 2. Save Guest
    guest_serializer = save_guest(data=data, user=user)
    guest_serializer.save(user=user)
    data= guest_serializer.data
    final_data = {
        **user_serializer.data,
        **guest_serializer.data,
    }
    print(final_data)
    return final_data


def save_guest(data, user: User):
    guest = getattr(user, "guest_profile", None)

    if guest:
        serializer = GuestSerializer(instance=guest, data=data, partial=True)
    else:
        serializer = GuestSerializer(data=data)

    serializer.is_valid(raise_exception=True)
    return serializer


def save_user(data, user: User | None = None):
    if user:
        serializer = UserSerializer(instance=user, data=data, partial=True)
    else:
        serializer = UserSerializer(data=data)

    serializer.is_valid(raise_exception=True)
    return serializer
