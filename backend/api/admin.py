from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register([PVA, Obligation, Task, TaskSchedule, ResponsibilityType, MedicinalProduct, Comment])