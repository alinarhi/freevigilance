from django.db import models
from django.contrib.auth.models import User
from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField

class ResponsibilityType(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return f"{self._meta.verbose_name} #{self.pk}"
    
    class Meta:
        verbose_name = "Тип обязательства"
        verbose_name_plural = "Типы обязательств"

class MedicinalProduct(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self) -> str:
        return f"{self._meta.verbose_name} #{self.pk}"

    class Meta:
        verbose_name = "Лекарственный препарат"
        verbose_name_plural = "Лекарственные препараты"

class PVA(models.Model):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    ENDING = "ENDING"
    COMPLETED = "COMPLETED"
    PVA_STATUS_CHOICES = [
        (PLANNED, "Планируемый"),
        (ACTIVE, "Заключен"),
        (ENDING, "Завершающийся"),
        (COMPLETED, "Завершен")
    ]
    requisites = models.CharField(max_length=500)
    medicinal_products = models.ManyToManyField(MedicinalProduct)
    description = models.TextField(blank=True)
    pva_link = models.CharField(max_length=2048, blank=True)
    main_contract_link = models.CharField(max_length=2048, blank=True)
    status = models.CharField(choices=PVA_STATUS_CHOICES, default=PLANNED, max_length=20)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self._meta.verbose_name} #{self.pk}"
    
    class Meta:
        verbose_name = "Договор"
        verbose_name_plural = "Договоры"


class Obligation(models.Model):
    pva = models.ForeignKey(PVA, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    responsibility_type = models.ForeignKey(ResponsibilityType, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self._meta.verbose_name} #{self.pk}"
    
    class Meta:
        verbose_name = "Обязательство"
        verbose_name_plural = "Обязательства"


class TaskSchedule(models.Model):
    DAILY = 'D'
    WEEKLY = 'W'
    MONTHLY = 'M'
    YEARLY = 'Y'
    FREQUENCY_CHOICES = [
        (DAILY, 'Ежедневно'),
        (WEEKLY, 'Каждую неделю'),
        (MONTHLY, 'Каждый месяц'),
        (YEARLY, 'Каждый год')
    ]
    frequency_type = models.CharField(
        choices=FREQUENCY_CHOICES,
        default=DAILY,
        max_length=1
    )
    day_of_week = models.IntegerField(blank=True, null=True)
    week_of_month = models.IntegerField(blank=True, null=True)
    day_of_month = models.IntegerField(blank=True, null=True)
    month_of_year = models.IntegerField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    
    class Meta:
        verbose_name = "Расписание"
        verbose_name_plural = "Расписания"

class Task(models.Model):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    HIDDEN = "HIDDEN"
    TASK_STATUS_CHOICES = [
        (NOT_STARTED, "Не начата"),
        (IN_PROGRESS, "В работе"),
        (COMPLETED, "Завершена"),
        (HIDDEN, "Скрыта")
    ]
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assigned_tasks', blank=True, null=True)
    schedule = models.ForeignKey(TaskSchedule, on_delete=models.SET_NULL, related_name='tasks', blank=True, null=True)
    obligation = models.ForeignKey(Obligation, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(choices=TASK_STATUS_CHOICES, default=NOT_STARTED, max_length=20)
    deadline = models.DateTimeField()
    is_recurring = models.BooleanField(default=False)
    completion_evidence_link = models.CharField(max_length=2048, blank=True)

    def __str__(self) -> str:
        return f"{self._meta.verbose_name} #{self.pk}"
    
    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['deadline']),
            models.Index(fields=['assigned_to', 'status', 'deadline']),
        ]

class Comment(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    def __str__(self) -> str:
        return f"{self._meta.verbose_name} #{self.pk}"
    
    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"



