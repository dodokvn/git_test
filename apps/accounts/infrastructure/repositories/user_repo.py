from django.contrib.auth import get_user_model, authenticate
from apps.accounts.domain.entities import UserEntity

User = get_user_model()


def user_exists(**kwargs) -> bool:
    return User.objects.filter(**kwargs).exists()


def create_user_entity(username, email, phone_number, password) -> UserEntity:
    user = User.objects.create_user(
        username=username,
        email=email,
        phone_number=phone_number,
        password=password,
    )
    return UserEntity(
        id=user.id,
        username=user.username,
        email=user.email,
        phone_number=user.phone_number,
    )


def authenticate_user(username, password) -> UserEntity:
    user = authenticate(username=username, password=password)
    if not user:
        return None
    return UserEntity(
        id=user.id,
        username=user.username,
        email=user.email,
        phone_number=user.phone_number,
    )
