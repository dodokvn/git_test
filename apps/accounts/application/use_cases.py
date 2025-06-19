from typing import Optional
from apps.accounts.domain.entities import UserEntity


def register_user_use_case(
    username: str,
    email: str,
    phone_number: str,
    password: str,
    user_exists: callable,
    create_user_entity: callable,
) -> UserEntity:
    """
    Enregistre un nouvel utilisateur après vérification.
    Les fonctions d'accès aux données sont injectées.
    """
    if user_exists(username=username):
        raise ValueError("Nom d'utilisateur déjà utilisé.")
    if user_exists(email=email):
        raise ValueError("Email déjà utilisé.")
    if user_exists(phone_number=phone_number):
        raise ValueError("Numéro déjà utilisé.")

    return create_user_entity(username, email, phone_number, password)


def login_user_use_case(
    username: str,
    password: str,
    authenticate_user: callable,
) -> Optional[UserEntity]:
    """
    Vérifie les identifiants utilisateur.
    """
    user = authenticate_user(username=username, password=password)
    if not user:
        raise ValueError("Identifiants invalides.")
    return user
