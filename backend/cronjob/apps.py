# cronjob/apps.py

from django.apps import AppConfig
from .scheduler import start
import os
from dotenv import load_dotenv


class CronjobConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cronjob"

    def ready(self):
        load_dotenv()
        print(os.environ.get("ENABLE_SCHEDULER"))
        # Check if the script is running in the main process
        if os.environ.get("RUN_MAIN") == "true":
            # Check if the scheduler should be enabled
            if os.environ.get("ENABLE_SCHEDULER") == "true":
                print("Starting scheduler...")
                start()
