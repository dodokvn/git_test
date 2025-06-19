from transfer_currency.infrastructure.models import Wallet


class DjangoWalletRepository:
    def get_wallet(self, user_id):
        return Wallet.objects.get(user__id=user_id)

    def save(self, wallet):
        wallet.save()
