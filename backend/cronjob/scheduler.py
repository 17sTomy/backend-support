from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
import time
from db import get_db
from utils import run_ai, generate_file_url
from django.conf import settings

logging.basicConfig()
logging.getLogger("apscheduler").setLevel(logging.DEBUG)


def processCalls():
    print("Starting job, connecting to mongo")
    db = get_db()
    print("Fetching")
    pending_call = db["calls"].find_one({"estado": "Pendiente"})
    print("Fetched")
    if pending_call is not None:
        print(f"Processing call {pending_call['_id']}")
        url = generate_file_url(
            account_name=settings.AZURE_ACCOUNT_NAME,
            account_key=settings.AZURE_ACCOUNT_KEY,
            container_name=settings.AZURE_STORAGE_CONTAINER_NAME,
            file_name=pending_call["filename"],
        )
        db["calls"].update_one(
            {"_id": pending_call["_id"]}, {"$set": {"estado": "Procesando"}}
        )
        run_ai(url, pending_call["_id"])
        print(f"Call {pending_call['_id']} finished")
        print(f"Updating call {pending_call['_id']} status")
        db["calls"].update_one(
            {"_id": pending_call["_id"]}, {"$set": {"estado": "Terminado"}}
        )
        print(f"Call {pending_call['_id']} status updated")
    else:
        print("No pending calls")
        return


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(processCalls, IntervalTrigger(seconds=10))
    scheduler.start()
