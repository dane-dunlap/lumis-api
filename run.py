from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from app import app
from app.routes import process_due_alerts
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import os

scheduler = BackgroundScheduler()

#def setup_scheduler():
    #scheduler.add_job(
        #func=process_due_alerts,
        #trigger=IntervalTrigger(minutes=1),  # Run every minute
        #name='Lumis Daily Job',
        #replace_existing=True)
    #scheduler.start()

#def schedule_jobs():
    
    #scheduler.add_job(
        #func=process_due_alerts,
        #trigger=CronTrigger(hour=8, minute=0),  # Run daily at 8 AM
        #name='Lumis Daily Job',
        #replace_existing=True)
    #scheduler.start()

#def shutdown_and_remove_jobs():
    #scheduler.remove_all_jobs()
    #scheduler.shutdown()

#atexit.register(shutdown_and_remove_jobs)

if __name__ == '__main__':
    #setup_scheduler()
     app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

