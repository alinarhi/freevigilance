from rest_framework import serializers
from .models import *
from auditlog.models import LogEntry

class TaskStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Task.TASK_STATUS_CHOICES, required=True)
    completion_evidence_link = serializers.CharField(max_length=2048, required=False)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ['username', 'is_staff', 'is_superuser', 'is_active', 'date_joined', 'last_login']
        exclude = ['groups', 'user_permissions']

class TaskScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskSchedule
        fields = '__all__'

class ObligationSerializer(serializers.ModelSerializer):
    pva_display = serializers.SlugRelatedField(slug_field='requisites', read_only=True, source='pva')
    responsibility_type = serializers.SlugRelatedField(slug_field='title', queryset=ResponsibilityType.objects.all(), required=False)
    class Meta:
        model = Obligation
        fields = '__all__'

class ResponsibilityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponsibilityType
        fields = '__all__'

class MedicinalProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicinalProduct
        fields = '__all__'

class PVASerializer(serializers.ModelSerializer):
    medicinal_products = serializers.SlugRelatedField(slug_field='title', many=True, queryset=MedicinalProduct.objects.all(), required=False)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
   
    class Meta:
        model = PVA
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    created_by_display = serializers.CharField(source='created_by.get_full_name', read_only=True)
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['created_by', 'task']

class LogEntrySerializer(serializers.ModelSerializer):
    actor_display = serializers.CharField(source='actor.get_full_name', read_only=True)
    content_type = serializers.SlugRelatedField(slug_field='model', read_only=True)
    content_type_display = serializers.SlugRelatedField(slug_field='name', read_only=True, source='content_type')
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    class Meta:
        model = LogEntry
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    schedule = TaskScheduleSerializer(required=False)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_display = serializers.CharField(source='created_by.get_full_name', read_only=True)
    assigned_to_display = serializers.CharField(source='assigned_to.get_full_name', read_only=True)

    obligation_display = serializers.CharField(source='obligation.title', read_only=True,)
    pva_display = serializers.CharField(source='obligation.pva.requisites', read_only=True)
    responsibility_type_display = serializers.CharField(source='obligation.responsibility_type.title', read_only=True)        
        
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['status', 'created_by']
        
    def create(self, validated_data):
        schedule_data = validated_data.pop('schedule', None)
        if schedule_data:
            schedule = TaskSchedule.objects.create(**schedule_data)
            task = Task.objects.create(schedule=schedule, **validated_data)
        else:
            task = Task.objects.create(**validated_data)
        return task
    
    def update(self, instance, validated_data):
        schedule_data = validated_data.pop('schedule', None)
        print(schedule_data)
        if schedule_data and validated_data.get('is_recurring'):
            if not instance.schedule:
                instance.schedule = TaskSchedule.objects.create(**schedule_data)
            else:
                for attr, value in schedule_data.items():
                    setattr(instance.schedule, attr, value)
            instance.schedule.save()
        elif instance.schedule and not validated_data.get('is_recurring'):
                old_schedule = instance.schedule
                instance.schedule = None
                if old_schedule.tasks.count() == 0:
                    old_schedule.delete()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance