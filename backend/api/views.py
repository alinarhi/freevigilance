from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status
from .filters import *
from .models import *
from .serializers import *
from .permissions import IsSelf
from .services import create_recurring_task_iteration
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter
from auditlog.models import LogEntry
from auditlog.context import disable_auditlog
from auditlog.diff import model_instance_diff

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'me']:
            permission_classes = [IsAuthenticated, IsSelf]
        elif self.action in ['create', 'destroy', 'update', 'partial_update']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = []

        return [permission() for permission in permission_classes]
    
    @action(detail=False)
    def me(self, request, pk=None):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_class = TaskFilter

    def get_permissions(self):
        if self.action=='destroy':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        return (
            Task.objects
            .select_related(
                'created_by',
                'assigned_to',
                'schedule',
                'obligation',
                'obligation__pva',
                'obligation__responsibility_type'
            ).exclude(status=Task.HIDDEN)
            .order_by('deadline')
        )
    
    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)
    
    def update(self, request, *args, **kwargs):
        task = self.get_object()
        if task.status == Task.COMPLETED:
            return Response({'detail': 'Изменение завершенной задачи запрещено.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        task = self.get_object()
        if task.status == Task.COMPLETED:
            return Response({'detail': 'Изменение завершенной задачи запрещено.'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(responses=TaskSerializer(many=True))
    @action(detail=False)
    def completed(self, request):
        queryset = self.filter_queryset(
            self.get_queryset()
            .filter(status=Task.COMPLETED)
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(responses=TaskSerializer(many=True))
    @action(detail=False)
    def my(self, request):
        user = request.user
        queryset = self.filter_queryset(
            self.get_queryset()
            .filter(assigned_to=user)
            .exclude(status=Task.COMPLETED)
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(responses=TaskSerializer(many=True))
    @action(detail=False, url_path='my/completed')
    def my_completed(self, request):
        user = request.user
        queryset = self.filter_queryset(
            self.get_queryset()
            .filter(assigned_to=user, status=Task.COMPLETED)
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

    @extend_schema(request=TaskStatusSerializer, responses={200: None, 201: TaskSerializer})
    @action(detail=True, methods=['post'], url_path='change-status')
    def change_status(self, request, pk=None):
        task = self.get_object()
        if task.status == Task.COMPLETED:  
            return Response({'detail': 'Изменение завершенной задачи запрещено.'}, status=status.HTTP_403_FORBIDDEN)
        status_serializer = TaskStatusSerializer(data=request.data)
        if status_serializer.is_valid():
            new_status = status_serializer.validated_data['status']
            print(new_status)
            if new_status == Task.COMPLETED:
                task.completion_evidence_link = status_serializer.validated_data.get('completion_evidence_link', '')
                if task.is_recurring:
                    new_task = create_recurring_task_iteration(task)
                    if new_task.deadline.date() <= task.schedule.end_date: 
                        with disable_auditlog():
                            new_task.save()
                        LogEntry.objects.log_create(new_task,
                                                    actor=request.user,
                                                    action=LogEntry.Action.CREATE,
                                                    changes = model_instance_diff(None, new_task),
                                                    changes_text=f'Автоматически создана новая итерация повторяющейся задачи. ID предыдущей итерации: {task.id}.')
                        task_serializer = self.get_serializer(new_task)
                        task.status = new_status
                        task.assigned_to = request.user
                        task.save()
                        return Response(task_serializer.data, status=status.HTTP_201_CREATED)
            task.status = new_status
            task.assigned_to = request.user
            task.save()
            return Response({'detail': f'Статус задачи обновлен: {task.status}.'}, status=status.HTTP_200_OK)
        else:
            return Response(status_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObligationViewSet(viewsets.ModelViewSet):
    queryset = Obligation.objects.select_related('pva', 'responsibility_type')
    serializer_class = ObligationSerializer
    filterset_class = ObligationFilter

@extend_schema(tags=['tasks'])
class ObligationTaskListView(generics.ListAPIView):
    serializer_class = TaskSerializer
    filterset_class = TaskFilter

    def get_queryset(self):
        obligation_id = self.kwargs['id']
        obligation = get_object_or_404(Obligation, id=obligation_id)
        return Task.objects.filter(obligation=obligation).select_related(
                'created_by',
                'assigned_to',
                'schedule',
                'obligation',
                'obligation__pva',
                'obligation__responsibility_type'
            ).order_by('deadline')

class ResponsibilityTypeViewSet(viewsets.ModelViewSet):
    queryset = ResponsibilityType.objects.all()
    serializer_class = ResponsibilityTypeSerializer
    
    def get_queryset(self):
        return super().get_queryset().order_by('title')

class MedicinalProductViewSet(viewsets.ModelViewSet):
    queryset = MedicinalProduct.objects.all()
    serializer_class = MedicinalProductSerializer
    
    def get_queryset(self):
        return super().get_queryset().order_by('title')


class PVAViewSet(viewsets.ModelViewSet):
    queryset = PVA.objects.prefetch_related('medicinal_products')
    serializer_class = PVASerializer
    filterset_class = PVAFilter
    
@extend_schema(tags=['obligations'])
class PVAObligationListView(generics.ListAPIView):
    serializer_class = ObligationSerializer
    filterset_class = ObligationFilter

    def get_queryset(self):
        pva_id = self.kwargs['id']
        pva = get_object_or_404(PVA, id=pva_id)
        return Obligation.objects.filter(pva=pva).select_related('pva', 'responsibility_type')


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
        return Comment.objects.filter(task=task).select_related('created_by').order_by('created_at')
    

class AuditlogListView(generics.ListAPIView):
    queryset = LogEntry.objects.select_related('actor', 'content_type').order_by('-timestamp')
    serializer_class = LogEntrySerializer
    filterset_class = LogEntryFilter


class TaskChangelogListView(generics.ListAPIView):
    serializer_class = LogEntrySerializer
    filterset_class = LogEntryFilter

    def get_queryset(self):
        task = get_object_or_404(Task, id=self.kwargs['id'])
        return LogEntry.objects.get_for_object(task).select_related('actor', 'content_type').order_by('-timestamp')