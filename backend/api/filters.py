from django_filters import rest_framework as filters
from .models import Task

class TaskFilter(filters.FilterSet):
    class Meta:
        model = Task
        fields = {
            'title': ['icontains'],
            'description': ['icontains'],
            'deadline': ['range'],
            'assigned_to__last_name': ['icontains'],
            'assigned_to__username': ['iexact'],
            'created_by__last_name': ['icontains'],
            'created_by__username': ['iexact'],
            'obligation__responsibility_type__title': ['iexact'],
            'obligation__start_date': ['gte'],
            'obligation__end_date': ['lte'],
            'title': ['icontains'],
            'status': ['exact']
        }
