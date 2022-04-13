from django.contrib.auth.models import User
from joggerlogger.models import Account
from django.db.models import Max, Sum
from datetime import datetime, timedelta

# Allows functions below to take user or account
# as input. Converts user to it's account
def user_or_account_to_account(func):
    def wrap(*args, **kwargs):
        if isinstance(args[0], Account):
            return func(args[0])
        if isinstance(args[0], User):
            return func(args[0].account.first())
        return -1
    return wrap


def get_stats(user):
    return (weekly_milage(user), total_milage(user),  longest_run(user))

# Sum of all distance ran by user
@user_or_account_to_account
def total_milage(user):
    total = 0
    for run in user.runs.all():
        total += run.distance
    return total

# Longest distance logged by user in one run
@user_or_account_to_account
def longest_run(user):
    return user.runs.all().aggregate(Max('distance'))['distance__max']

# Weekly milage of the last year. Only counts
# weeks after the first logged run
@user_or_account_to_account
def weekly_milage(user):
    if len(user.runs.all()) == 0:
        return 0
    first_run_date = user.runs.first().date

    monday_then = (first_run_date - timedelta(days=first_run_date.weekday()))
    monday_now  = (datetime.now() - timedelta(days=datetime.now().weekday())).date()
    

    weeks = (monday_now - monday_then).days // 7 + 1
    return user.runs.all().aggregate(Sum('distance'))['distance__sum'] / weeks
