from celery.schedules import crontab
from app.tasks import celery, send_daily_reminders, generate_monthly_report

# Configure periodic tasks
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Send daily reminders at 7:00 PM every day
    sender.add_periodic_task(
        crontab(hour=19, minute=0),
        send_daily_reminders.s(),
        name='send daily reminders'
    )
    
    # Generate monthly reports on the 1st of every month at 6:00 AM
    sender.add_periodic_task(
        crontab(day_of_month=1, hour=6, minute=0),
        generate_monthly_report.s(),
        name='generate monthly reports'
    )

if __name__ == '__main__':
    print("Scheduled tasks set up:")
    print("1. Daily reminders: 7:00 PM every day")
    print("2. Monthly reports: 6:00 AM on the 1st of every month")