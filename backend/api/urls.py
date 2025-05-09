from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'obligations', ObligationViewSet)
router.register(r'responsibility-types', ResponsibilityTypeViewSet)
router.register(r'medicinal-products', MedicinalProductViewSet)
router.register(r'pvas', PVAViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('obligations/<int:id>/tasks/', ObligationTaskListView.as_view(), name='obligation-tasks'),
    path('pvas/<int:id>/obligations/', PVAObligationListView.as_view(), name='pva-tasks'),
    path('tasks/<int:id>/comments/', CommentListCreateView.as_view(), name='task-comments'),
    path('tasks/<int:id>/changelog/', TaskChangelogListView.as_view(), name='task-changelog'),
    path('auditlog/', AuditlogListView.as_view())
]

