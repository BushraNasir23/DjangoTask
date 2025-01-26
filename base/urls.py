from django.urls import path
from .views import (
    ProjectDetailView,
    ProjectListCreateAPIView,
    ProjectRetrieveUpdateDestroyAPIView,
    TaskListCreateAPIView,
    TaskRetrieveUpdateDestroyAPIView,
    ApproveTaskView,
    RevokeApprovalView,
    PendingTasksView
    
)

urlpatterns = [
    path('projects/', ProjectListCreateAPIView.as_view(), name='project_create_list'),
    path('projects/<int:pk>/', ProjectRetrieveUpdateDestroyAPIView.as_view(), name='project_get_update'),
    path('project_details/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),

    path('tasks/', TaskListCreateAPIView.as_view(), name='task_create_list'),
    path('tasks/<int:pk>/', TaskRetrieveUpdateDestroyAPIView.as_view(), name='tasks_get_update'),


    path('approve/<int:task_id>/', ApproveTaskView.as_view(), name='approve_task'),
    path('revoke/<int:task_id>/', RevokeApprovalView.as_view(), name='revoke_approval'),
    path('tasks/pending/', PendingTasksView.as_view(), name='pending-tasks')
]


