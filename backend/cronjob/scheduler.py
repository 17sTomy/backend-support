from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
import time

logging.basicConfig()
logging.getLogger("apscheduler").setLevel(logging.DEBUG)


def processCalls():
    print("Hello World, jobs started!")
    time.sleep(20)
    print("Hello World, jobs done!")


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(processCalls, IntervalTrigger(seconds=10))
    scheduler.start()
