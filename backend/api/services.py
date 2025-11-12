from .models import Task, TaskSchedule, MedicinalProduct
import copy
from datetime import datetime, timedelta
import calendar

def create_recurring_task_iteration(task: Task):
    new_task = copy.copy(task)
    new_task.id = None
    new_task.status = Task.NOT_STARTED
    new_task.completion_evidence_link = ""

    schedule = task.schedule
    match schedule.frequency_type:
        case TaskSchedule.DAILY:
            new_task.deadline = task.deadline + timedelta(days=1)
        case TaskSchedule.WEEKLY:
            new_task.deadline = task.deadline + timedelta(weeks=1)
        case TaskSchedule.MONTHLY:
            if task.deadline.month == 12:
                year = task.deadline.year+1
                month = 1
            else:
                year = task.deadline.year 
                month = task.deadline.month + 1
            new_task.deadline = task.deadline.replace(year=year, month=month, day=min(calendar.monthrange(year, month)[1], task.deadline.day))      
        case TaskSchedule.YEARLY:
                new_task.deadline = task.deadline.replace(year=task.deadline.year+1)
    return new_task