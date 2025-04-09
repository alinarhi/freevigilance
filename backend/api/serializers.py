from rest_framework import serializers
from .models import TaskSchedule, Task, User, Obligation, ResponsibilityType, MedicinalProduct, Partner, PVA, Comment
from auditlog.models import LogEntry

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = ['id', 'username', 'first_name', 'last_name', 'email', 'last_login']
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}
        

class TaskScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskSchedule
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    # TODO nest schedule
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_by']


class ObligationSerializer(serializers.ModelSerializer):
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

class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = '__all__'

class PVASerializer(serializers.ModelSerializer):
    class Meta:
        model = PVA
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['created_by', 'task']

class LogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEntry
        fields = '__all__'
