from .common_settings import *  # noqa: F401,F403

try:
    from .local_settings import *  # noqa: F401,F403
except ImportError:
    # En prod, tu peux lever une erreur explicite
    raise RuntimeError("local_settings.py manquant !")
