from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics

from .filters import TaskFilter
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .permissions import IsSelfOrReadOnly
from rest_framework.decorators import action
from django_filters import rest_framework as filters
from auditlog.models import LogEntry


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsSelfOrReadOnly]
        elif self.action in ['create', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []

        return [permission() for permission in permission_classes]
        
# class UserListCreateView(generics.ListCreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


# TODO: task schedule?

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_class = TaskFilter

    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)
    
    @action(detail=True)
    def changelog(self, request, pk=None):
        task = self.get_object()
        changelog = LogEntry.objects.get_for_object(task)
        serializer = LogEntrySerializer(changelog, many=True)
        return Response(serializer.data)
    
    @action(detail=False)
    def assigned(self, request):
        user = request.user
        queryset = Task.objects.filter(assigned_to=user).exclude(status=Task.COMPLETED).order_by('-deadline')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ObligationViewSet(viewsets.ModelViewSet):
    queryset = Obligation.objects.all()
    serializer_class = ObligationSerializer

# List or List create?
class ObligationTaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        obligation_id = self.kwargs['id']
        obligation = get_object_or_404(Obligation, id=obligation_id)
        return Task.objects.filter(obligation=obligation)

class ResponsibilityTypeViewSet(viewsets.ModelViewSet):
    queryset = ResponsibilityType.objects.all()
    serializer_class = ResponsibilityTypeSerializer

class MedicinalProductViewSet(viewsets.ModelViewSet):
    queryset = MedicinalProduct.objects.all()
    serializer_class = MedicinalProductSerializer

class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer

class PVAViewSet(viewsets.ModelViewSet):
    queryset = PVA.objects.all()
    serializer_class = PVASerializer

class PVAObligationListView(generics.ListAPIView):
    serializer_class = ObligationSerializer

    def get_queryset(self):
        pva_id = self.kwargs['id']
        pva = get_object_or_404(PVA, id=pva_id)
        return Obligation.objects.filter(pva=pva)


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_task(self):
        task_id = self.kwargs['id']
        task = get_object_or_404(Task, id=task_id)
        return task
    
    def perform_create(self, serializer):
        task = self.get_task()
        return serializer.save(created_by=self.request.user, task=task)
    
    def get_queryset(self):
        task = self.get_task()
        return Comment.objects.filter(task=task).order_by('created_at')
    

class AuditlogListView(generics.ListAPIView):
    queryset = LogEntry.objects.all().order_by('-timestamp')
    serializer_class = LogEntrySerializer
    
# retrieve destroy
# class CommentView(generics.DestroyAPIView):