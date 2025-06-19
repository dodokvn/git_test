import threading
import time

from django.apps import AppConfig
from django.core.management import call_command


class TransferCurrencyConfig(AppConfig):
    # default_auto_field = "django.db.models.BigAutoField"
    name = "apps.transfer_currency"

    def ready(self):
        # Start a thread to run the scheduled transaction checker
        def run_scheduled_transactions():
            while True:
                try:
                    # Call the management command
                    call_command("check_scheduled_transactions")
                    print("Scheduled transactions checked successfully.")
                except Exception as e:
                    print(f"Error running scheduled transactions: {e}")
                # Wait for 10 seconds before running again
                time.sleep(10)

        # Start the thread
        thread = threading.Thread(target=run_scheduled_transactions, daemon=True)
        thread.start()
