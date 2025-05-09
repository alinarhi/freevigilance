from django_filters import rest_framework as filters
from .models import Task, PVA, Obligation
from auditlog.models import LogEntry

class TaskFilter(filters.FilterSet):
    # status = filters.ChoiceFilter(Task.STATUS_CHOICES)
    class Meta:
        model = Task
        fields = {
            'title': ['icontains'],
            'status': ['exact'],
            'description': ['icontains'],
            'deadline': ['gte', 'lte'],
            'assigned_to': ['exact'],
            'assigned_to__last_name': ['icontains'],
            'assigned_to__username': ['iexact'],
            'created_by__last_name': ['icontains'],
            'created_by__username': ['exact'],
            'obligation': ['exact'],
            'obligation__responsibility_type__title': ['iexact'],
        }

class ObligationFilter(filters.FilterSet):
    class Meta:
        model = Obligation
        fields = {
            'pva': ['exact'],
            'title': ['icontains'],
            'description': ['icontains'],
            'responsibility_type__title': ['iexact'],
        }

class PVAFilter(filters.FilterSet):
    class Meta:
        model = PVA
        fields = {
            'requisites': ['icontains'],
            'medicinal_products__title': ['icontains'],
            'status': ['exact'],
        }
        

class LogEntryFilter(filters.FilterSet):
    class Meta:
        model = LogEntry
        fields = {
            'action': ['exact'],
            'object_id': ['exact'],
            'content_type__model': ['iexact'],
            'actor__username': ['iexact'],
            'actor__last_name': ['icontains'],
            'timestamp': ['gte', 'lte'],
        }