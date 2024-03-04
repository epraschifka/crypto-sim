# updater.py
from datetime import datetime
from apscheduler.schedulers.background import BlockingScheduler
from priceUpdater import getPricesApi

def start():
    scheduler = BlockingScheduler()
    scheduler.add_job(getPricesApi.func, "interval", minutes=5)
    scheduler.start()

if __name__ == "__main__":
    start()
