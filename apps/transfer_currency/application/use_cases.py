from __future__ import annotations

from datetime import datetime

from transfer_currency.domain.entities import TransactionEntity, WalletEntity


def execute_transfer(transaction: TransactionEntity) -> bool:
    """Valide les règles générales d’un transfert."""
    if transaction.amount <= 0:
        raise ValueError("Le montant doit être supérieur à 0")
    # 🔒 ajouter ici d’autres règles globales
    return True


def perform_transfer(
    sender: WalletEntity,
    receiver: WalletEntity,
    amount: float,
    event: str,
) -> TransactionEntity:
    """Met à jour les soldes in-memory et renvoie une entité Transaction."""
    if amount <= 0:
        raise ValueError("Le montant doit être supérieur à 0")
    if sender.balance < amount:
        raise ValueError("Solde insuffisant")

    sender.balance -= amount
    receiver.balance += amount

    return TransactionEntity(
        id=0,  # sera rempli par la persistance
        sender_wallet_id=sender.id,
        receiver_wallet_id=receiver.id,
        amount=amount,
        event=event,
        status="completed",
        timestamp=datetime.now(),
    )
