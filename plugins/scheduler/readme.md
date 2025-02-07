[apscheduler.triggers.cron — APScheduler 3.10.4.post1 documentation](https://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html?highlight=cron#examples)

date
    weeks (float) – number of weeks to wait
    days (float) – number of days to wait
    hours (float) – number of hours to wait
    minutes (float) – number of minutes to wait
    seconds (float) – number of seconds to wait
    microseconds (float) – number of microseconds to wait
    start_time (Any) – first trigger date/time (defaults to current date/time if omitted)
    end_time (Optional[Any]) – latest possible date/time to trigger on

cron
    year (int|str) – 4-digit year
    month (int|str) – month (1-12)
    day (int|str) – day of month (1-31)
    week (int|str) – ISO week (1-53)
    day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
    hour (int|str) – hour (0-23)
    minute (int|str) – minute (0-59)
    second (int|str) – second (0-59)
    start_date (datetime|str) – earliest possible date/time to trigger on (inclusive)
    end_date (datetime|str) – latest possible date/time to trigger on (inclusive)
    timezone (datetime.tzinfo|str) – time zone to use for the date/time calculations (defaults to scheduler timezone)
    jitter (int|None) – delay the job execution by jitter seconds at most

interval
    years (int) – number of years to wait
    months (int) – number of months to wait
    weeks (int) – number of weeks to wait
    days (int) – number of days to wait
    hour (int) – hour to run the task at
    minute (int) – minute to run the task at
    second (int) – second to run the task at
    start_date (Any) – first date to trigger on (defaults to current date if omitted)
    end_date (Optional[Any]) – latest possible date to trigger on
    timezone (Any) – time zone to use for calculating the next fire time
